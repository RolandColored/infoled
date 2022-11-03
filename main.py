import configparser
import logging
import os
import signal
import sys
import time
from logging.config import fileConfig

import requests

from display import Display


def signal_handler(sig, frame):
    logging.info(f'Signal {sig} received')
    display.print('Bye')
    display.cleanup()
    sys.exit(0)


def current_temperature() -> str:
    api_key = os.environ['WEATHER_API_KEY']
    lat, lon = config['weather']['latitude'], config['weather']['longitude']
    response = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}')
    if not response.ok:
        return 'ERROR'
    temp_value = response.json()['main']['temp']
    return f'{temp_value:.0f} C'


if __name__ == "__main__":
    fileConfig('logging.ini')
    config = configparser.ConfigParser()
    config.read('config.ini')

    display = Display(config['led'].getint('width'), config['led'].getint('height'))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        display.print(current_temperature())
        time.sleep(60)
