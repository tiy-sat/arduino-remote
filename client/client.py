from config import SERVER, USB_DEVICE, DEVICE_CONFIG

import sys

import serial
from serial.tools import list_ports
import requests
import json

reconnects = 5

base_url = '{proto}://{host}:{port}'.format(**SERVER)
requests.post(base_url + '/config', json=DEVICE_CONFIG)

got_config = requests.get(base_url + '/config').json()
print('GOT:' + str(got_config))

try:
    serial.Serial(USB_DEVICE, timeout=5)
except serial.serialutil.SerialException:
    print("Could not open port: " + USB_DEVICE)
    print("Perhaps plug in your device or set config.USB_DEVICE to one of these: ")
    print('\n'.join([ port[0] for port in list_ports.comports() ]))
    sys.exit()

while reconnects:
    with serial.Serial(USB_DEVICE, timeout=5) as serial_port:
        # serial_port.write(b'')
        # serial_port.readline()

        pass

    reconnects = reconnects - 1
