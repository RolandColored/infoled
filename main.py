import configparser
import logging
import os
import signal
import sys
import time
from logging.config import fileConfig
from typing import Union

import requests
import spotipy
from cachetools.func import ttl_cache
from spotipy.oauth2 import SpotifyOAuth

from display import Display


def signal_handler(sig, frame):
    logging.info(f'Signal {sig} received')
    display.cleanup()
    sys.exit(0)


@ttl_cache(ttl=60*60)
def current_temperature() -> str:
    api_key = os.environ['WEATHER_API_KEY']
    lat, lon = config['weather']['latitude'], config['weather']['longitude']
    response = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}')
    if not response.ok:
        return 'ERROR'
    temp_value = response.json()['main']['temp']
    return f'{temp_value:.0f} C'


@ttl_cache(ttl=60)
def current_music() -> Union[str, None]:
    scope = 'user-read-playback-state'
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

    result = spotify.currently_playing()
    if result is not None:
        try:
            return f"{result['item']['artists'][0]['name']} - {result['item']['name']}"
        except (TypeError, KeyError):
            return None
    else:
        return None


if __name__ == "__main__":
    fileConfig('logging.ini')
    config = configparser.ConfigParser()
    config.read('config.ini')

    display = Display(config['led'].getint('width'), config['led'].getint('height'))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        try:
            text = current_music()
            if text is None:
                text = current_temperature()

            display.print(text)
            time.sleep(2)
        except Exception as e:
            display.print(e.message)
