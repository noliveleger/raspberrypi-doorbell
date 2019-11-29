# -*- code utf-8 -*-
from signal import pause

from app.config import logger
from app.helpers.button import Button
from app.threads.day_light_toggle import DayLightToggle
from app.threads.message_broker import MessageBroker

from .base import BaseService


class Daemon(BaseService):

    @staticmethod
    def start(**kwargs):
        # Init button & leds
        Button()

        # Start Day Light
        day_light_toggle = DayLightToggle()
        day_light_toggle.start()

        # Listen for messages through socket (e.g. Amazon Dash Button/Back Door)
        message_broker = MessageBroker()
        message_broker.start()

        logger.info('Daemon is started!')

        try:
            pause()
        except (SystemExit, KeyboardInterrupt):
            pass

        logger.debug('Cleaning up...')
        MessageBroker.stop()
        logger.info('Daemon has been stopped')
