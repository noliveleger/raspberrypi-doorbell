# -*- code utf-8 -*-
from signal import pause

from app.config import logger
from app.devices.button import Button
from app.helpers.sundial import Sundial
from app.threads.cron import Cron
from app.threads.message_broker import MessageBroker

from . import BaseCommand


class Daemon(BaseCommand):

    @staticmethod
    def start(**kwargs):
        # `Sundial` is a singleton and must be called BEFORE all other singleton
        # classes. Otherwise a lock will occur because of `@synchronized(lock)`
        # decorator.
        sundial = Sundial()
        logger.debug('{} mode activated'.format(sundial.human_readable_mode))

        # Initialize the button & its LEDs
        button = Button()

        # Start cron tasks
        cron = Cron()
        cron.start()

        # Listen for messages through socket (e.g. Amazon Dash Button/Back Door)
        message_broker = MessageBroker()
        message_broker.start()

        logger.warning('Daemon has been started')
        import time

        time.sleep(10)
        button.pressed()

        try:
            pause()
        except (SystemExit, KeyboardInterrupt):
            pass

        logger.debug('Cleaning up...')
        MessageBroker.stop()
        logger.warning('Daemon has been stopped')
