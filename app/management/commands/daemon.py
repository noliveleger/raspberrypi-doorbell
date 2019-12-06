# -*- code utf-8 -*-
from signal import pause

from app.config import logger
from app.devices.button import Button
from app.threads.cron import Cron
from app.threads.message_broker import MessageBroker

from . import BaseCommand


class Daemon(BaseCommand):

    @staticmethod
    def start(**kwargs):
        # Initialize the button & its LEDs
        button = Button()
        button.activate_led()

        # Start cron tasks
        cron = Cron()
        cron.start()

        # Listen for messages through socket (e.g. Amazon Dash Button/Back Door)
        message_broker = MessageBroker()
        message_broker.start()

        logger.warning('Daemon has been started')

        try:
            pause()
        except (SystemExit, KeyboardInterrupt):
            pass

        logger.debug('Cleaning up...')
        MessageBroker.stop()
        logger.warning('Daemon has been stopped')
