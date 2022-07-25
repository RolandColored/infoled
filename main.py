import configparser
import logging
import time

from luma.core.interface.serial import spi, noop
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT
from luma.core.render import canvas
from luma.led_matrix.device import max7219

config = configparser.ConfigParser()
config.read('config.ini')


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
        logging.info('Falling back to emulator')
    # start show
    try:
        temperature = '22 C'

        with canvas(device) as draw:
            text(draw, (4, 1), temperature, fill='white', font=proportional(CP437_FONT))
        time.sleep(5)

    except KeyboardInterrupt:
        logging.info('Shutting down')
        pass
