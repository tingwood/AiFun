#!/usr/bin/env python3

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging
import raspberrypi.pi_actions as pi
from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient


def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('water flower',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    with Board() as board:
        while True:
            board.button.wait_for_press()
            board.led.state = Led.ON
            while True:
                if hints:
                    logging.info('Say something, e.g. %s.' % ', '.join(hints))
                else:
                    logging.info('Say something.')
                text = client.recognize(language_code=args.language,
                                        hint_phrases=hints)
                if text is None:
                    logging.info('Sorry, You said nothing.')
                    continue

                logging.info('You said: "%s"' % text)
                text = text.lower()
                if 'water flower' in text:
                    logging.info('watering flower')
                    #pi.watering()
                elif 'goodbye' in text:
                    exit(0)
                board.led.state = Led.OFF
                break

if __name__ == '__main__':
    main()
