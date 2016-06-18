from config import SERVER, USB_DEVICE, DEVICE_CONFIG, LOG_CONFIG

import sys

import serial
from serial.tools import list_ports
import requests
import json
import logging

logging.basicConfig(**LOG_CONFIG)

reconnects = 5

device_config = DEVICE_CONFIG

base_url = '{proto}://{host}:{port}'.format(**SERVER)

def handle_events(serial_port):
    """Look for events from serial port, send to remote server."""
    line = serial_port.readline().decode('utf-8')
    logging.debug("LINE: " + str(line))

    if not line:
        return
        
    event = None

    try:
        event = json.loads(line)
        logging.info("EVENT: " + str(event))
    except json.decoder.JSONDecodeError:
        logging.warning("Invalid line: {0}".format(line)) # Sometimes will see mangled output when reconnecting

    if event:
        response = requests.post(base_url + '/events', json=event)
        if response.status_code != 200:
            logging.error("Request: {0}, Response: {1}, {2}".format(response.request.url, response.status, response.body))

    return

def handle_actions(serial_port):
    """Get actions from server and send them to serial port."""
    response = requests.get(base_url + '/actions')
    if response.status_code != 200:
        logging.error("Request: {0}, Response {1}, {2}".format(response.request.url, response.status, response.body))
    actions = response.json()['actions']

    for action in actions:
        logging.debug("ACTION: " + str(action))
        action_bytes = json.dumps(action).encode('utf-8')
        serial_port.write(action_bytes)

    return

def send_config(device_config):
    """Send device config to server."""

    try:
        requests.post(base_url + '/config', json=device_config)
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to {url}.".format(url=base_url))
        sys.exit()

    return

def test_serial_port(USB_DEVICE):
    try:
        with serial.Serial(USB_DEVICE, timeout=1) as serial_port_test:
            pass
    except serial.serialutil.SerialException:
        return False

    return True

if __name__ == '__main__':
    logging.debug('CONFIG:' + str(device_config))
    send_config(device_config)

    if not test_serial_port(USB_DEVICE):
        logging.critical("Could not open port: " + USB_DEVICE)
        logging.critical("Perhaps plug in your device or set config.USB_DEVICE to one of these: ")
        logging.critical('\n'.join([ port[0] for port in list_ports.comports() ]))
        sys.exit()

    reconnects = 5 # Try to reconnect to USB device up to this many times

    while reconnects:
        with serial.Serial(USB_DEVICE, timeout=5) as serial_port:
            while True:
                # Two steps in each loop:
                #  1) Read events from device and publish to server
                #  2) Read actions from server and publish to device

                handle_events(serial_port)
                handle_actions(serial_port)

        reconnects = reconnects - 1
