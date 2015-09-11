"""
Bridges UART over bluetooth LE to OSC
Heavily cribbed from uart_service.py example

Setup:
    install https://learn.adafruit.com/bluefruit-le-python-library/installation
    (if necessary to also install pyobjc, use easy_install, not pip)

    Make sure bluetooth module is in CMD not DATA

    % sudo pip install pyosc

    % python bluefruit_osc_bridge.py

"""

import heapq
import signal
import time

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

import OSC

# Get the BLE PROVIDER for the current platform.
PROVIDER = Adafruit_BluefruitLE.get_provider()
BASE_PORT = 8000 # First device will be port 8000, next 8001, etc.

interrupted = False # pylint: disable=invalid-name

class DeviceTracker(object):
    """ Keeps track of all known bluetooth devices """
    devices = set({})
    connections = []
    available_indices = []
    max_index = 0
    adapter = None

    def start(self):
        """ Reset any lingering bluetooth state """
        # Clear any cached data because both bluez and CoreBluetooth have issues
        # with caching data and it going stale.
        PROVIDER.clear_cached_data()

        # Get the first available BLE network adapter
        # and make sure it's powered on.
        self.adapter = PROVIDER.get_default_adapter()
        self.adapter.power_on()
        print 'Using adapter: {0}'.format(self.adapter.name)

        # Disconnect any currently connected UART devices.
        # Good for cleaning up and tarting from a fresh state.
        print 'Disconnecting any connected UART devices...'
        UART.disconnect_devices()
        self.adapter.start_scan()

    def next_index(self):
        try:
            return heapq.heappop(self.available_indices)
        except IndexError:
            self.max_index = self.max_index + 1
            return self.max_index - 1

    def add_device(self, device):
        index = self.next_index()
        print "Adding device: {0} at port {1}".format(device.id, 8000 + index)
        try:
            connection = Connection(device, index)
            self.connections.append(connection)
        except:
            print "Device wasn't a UART device. Ignoring"
            heapq.heappush(self.available_indices, connection.index)
        finally:
            self.devices.add(device)

    def remove_device(self, device):
        for connection in self.connections:
            if connection.device.id == device.id:
                print "Removing device: {0} at index {1}".format(device.id, connection.index)
                connection.close()
                heapq.heappush(self.available_indices, connection.index)
        self.connections = [c for c in self.connections if c.device.id != device.id]
        self.devices.remove(device)

    def update_device_list(self):
        found_devices = set(PROVIDER.find_devices())
        new_devices = found_devices - self.devices
        gone_devices = self.devices - found_devices

        for device in gone_devices:
            self.remove_device(device)

        for device in new_devices:
            self.add_device(device)

    def close(self):
        self.adapter.stop_scan()
        for connection in self.connections:
            self.remove_device(connection.device)

class Connection(object):
    """ Represents a bluetooth device input and its OSC output """

    def __init__(self, device, index):
        self.device = device
        self.osc = OSC.OSCClient()
        self.osc.connect(('127.0.0.1', 8000 + index))

        device.connect()
        UART.discover(self.device)

        self.uart = UART(self.device)
        self.index = index

    def close(self):
        """ Tears down the device """
        if self.device.is_connected:
            self.device.disconnect()
        self.osc.close()



def main():
    """
    Due to the way the Adafruit bluetooth library structures itself
    all bluetooth code needs to execute inside a function. When that
    function exits, the bluetooth session ends. This is that function
    """

    tracker = DeviceTracker()
    tracker.start()

    print "Started. Press Ctrl-C to stop listening."

    try:
        while not interrupted:
            tracker.update_device_list()

            for connection in tracker.connections:
                received = connection.uart.read(timeout_sec=1)
                if received is not None:
                    print 'Received: {0} from {1}'.format(received, connection.device.id) #pylint: disable=line-too-long
                    msg = OSC.OSCMessage()
                    msg.setAddress("/route")
                    msg.append(received)
                    try:
                        connection.osc.send(msg)
                    except OSC.OSCClientError:
                        print "Message send failed. Is max running?"

            time.sleep(1)
    finally:
        tracker.close()

# Setup our signal handler so we can catch Ctrl-C
def handler(signum, frame): # pylint: disable=unused-argument
    """ Make sure Ctrl-C gets caught """
    global interrupted # pylint: disable=global-statement,invalid-name
    print "Quitting..."
    interrupted = True

signal.signal(signal.SIGINT, handler)

# Initialize the BLE system.  MUST be called before other BLE calls!
PROVIDER.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
PROVIDER.run_mainloop_with(main)

