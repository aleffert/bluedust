## Setup ##

1. Follow https://learn.adafruit.com/bluefruit-le-python-library/installation to install adafruit bluetooth library

2. Install pyosc ``sudo pip install pyosc``

3. Make sure bluetooth module is in CMD not DATA

4. If not using serial, comment out line in sketch at start of ``setup`` that says ``COMMENT THIS OUT WHEN NOT USING SERIAL``.

## Running ##

```
% python ./bluefruit_osc_bridge.py
```


#####
Notes
#####

There are three files here:

1. An arduino sketch called ``bluedust``. Inside that sketch, there is also a header file, ``BluefruitConfig.h`` with some configuration information.

2. A very simple proof of concept max patch called ``udp-example.maxpat`` that listens for two different devices.

3. A python script ``bluefruit_os_bridge.py`` that does the bridging between bluetooth and max.

The arduino file has a block inside of the ``loop`` function marked with a comment that will need to be changed to send your sensor reading instead of the character "A".
