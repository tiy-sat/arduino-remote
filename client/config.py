import logging

SERVER = {
    'proto': 'http',
    'host': '127.0.0.1',
    'port': '8080'
}

USB_DEVICE = '/dev/cu.usbserial-DN01DIU1'

DEVICE_CONFIG = {
    'sources': ['arduino'],
    'targets': [],
    'local_mode': False
}

LOG_CONFIG = {
    'format': '%(asctime)s %(message)s',
    'datefmt': '%Y-%m-%d %I:%M:%S %p',
    'level': logging.INFO
}
