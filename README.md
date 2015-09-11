## Setup ##

1. Follow https://learn.adafruit.com/bluefruit-le-python-library/installation to install adafruit bluetooth library. If you need to follow the install pyobjc step here, then make sure to use the ``easy_install`` instructions and not the ``pip`` ones.

2. Install pyosc:
    ```
    sudo pip install pyosc
    ```

3. Make sure bluetooth module is in CMD not DATA

4. If not using serial, comment out line in sketch at start of ``setup`` that says ``COMMENT THIS OUT WHEN NOT USING SERIAL``.

## Running ##

1. Start your devices.

2. Open max

3. Run the following terminal command:

```
% python ./bluefruit_osc_bridge.py
```

The order you start max, arduino, and python should not matter.


## Notes ##

There are three files here:

1. An arduino sketch called ``bluedust``. Inside that sketch, there is also a header file, ``BluefruitConfig.h`` with some basic configuration information. This file will need to continue to be side by side with the ``.ino`` file.

2. A very simple proof of concept max patch called ``udp-example.maxpat`` that listens for data from two different devices over OSC and prints them to console.

3. A python script ``bluefruit_osc_bridge.py`` that does the bridging between bluetooth and max via OSC.

The arduino file has a block inside of the ``loop`` function marked with a comment that will need to be changed to send your sensor reading instead of the character "A".
