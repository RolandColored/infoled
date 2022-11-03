import configparser
import logging
import os
import time
from logging.config import fileConfig

import requests
from luma.core.interface.serial import spi, noop
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT
from luma.core.render import canvas
from luma.led_matrix.device import max7219

fileConfig('logging.ini')
config = configparser.ConfigParser()
config.read('config.ini')


def current_temperature():
    api_key = os.environ['WEATHER_API_KEY']
    lat, lon = config['weather']['latitude'], config['weather']['longitude']
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}')
    if not response.ok:
        return 'ERROR'
    temp_value = response.json()['main']['temp']
    return f'{temp_value:.0f} C'


if __name__ == "__main__":
    # create display device
    try:
        serial = spi(port=0, device=0, gpio=noop())
        device = max7219(serial, cascaded=4, block_orientation=90, rotate=2)
        print('Created device')
    except ModuleNotFoundError:
        from luma.emulator.device import pygame

        device = pygame(width=config['led'].getint('width'), height=config['led'].getint('height'),
                        mode='1', transform='led_matrix')
        device.contrast(60)
        logging.info('Falling back to emulator')

    # start show
    try:
        while True:
            with canvas(device) as draw:
                text(draw, (4, 1), current_temperature(), fill='white', font=proportional(CP437_FONT))
            time.sleep(60)

    except KeyboardInterrupt:
        logging.info('Shutting down')
