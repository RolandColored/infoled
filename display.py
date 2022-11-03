import logging

from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, textsize, show_message
from luma.core.legacy.font import proportional, CP437_FONT
from luma.core.render import canvas
from luma.led_matrix.device import max7219


class Display:
    font = proportional(CP437_FONT)

    def __init__(self, width: int, height: int):
        try:
            serial = spi(port=0, device=0, gpio=noop())
            self.device = max7219(serial, cascaded=4, block_orientation=90, rotate=2)
            self.device.contrast(5)
            logging.info('Created device')

        except ModuleNotFoundError:
            from luma.emulator.device import pygame
            self.device = pygame(width=width, height=height, mode='1', transform='led_matrix')
            logging.info('Falling back to emulator')

        self.print('Hello world')

    def print(self, message: str):
        text_width, _ = textsize(message, self.font)
        padding = (self.device.size[0] - text_width) / 2

        if padding > 0:
            with canvas(self.device) as draw:
                text(draw, (padding, 0), message, fill='white', font=self.font)
        else:
            show_message(self.device, message, y_offset=0, fill='white', font=self.font, scroll_delay=0.1)

    def cleanup(self):
        self.device.cleanup()
