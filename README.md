## Arduino Remote

Arduino Remote is a demo of connecting an Arduino device to the web with Python. This code is for demo purposes only, and is not suitable for real-world or production use.

### controller

`controller.ino` is an Arduino program, and needs to be loaded onto the target Arduino or compatible device using the [Arduino IDE](https://www.arduino.cc/en/Main/Software) or similar tool. It sends events and receives actions over the serial port.

### client

`client.py` is a Python 3 program that connects to a device over the serial port configured in `config.py`. It sends events and receives actions, acting as a proxy to the server.

### server

`arduino_remote.py` is a web server written in bottle. It provides a RESTish API for events an actions.

## Getting it to work

1. Obtain an Arduino compatible device.
2. Install and run the Arduino IDE
3. Connect the device to your computer.
4. Upload `controller.ino` to the Arduino.
5. Configure `config.py` to match your system.
6. Run `client.py` with Python 3 (use virtualenv).
7. Run `arduino_remote.py` with Python 3 (use a different virtualenv).
8. Send actions to your server as JSON, and receive events from it, also as JSON.
