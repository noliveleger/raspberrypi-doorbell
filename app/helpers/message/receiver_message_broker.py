# -*- code utf-8 -*-
from app.config import logger
from app.threads.cron import Cron

from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'message_broker'

    @classmethod
    def read(cls, message, last_time_received):
        if message['action'] == cls.STOP:
            # Stop `Cron`'s inner thread
            cron = Cron()
            cron.stop()

            # stop server and its thread. Must be the last thing to stop
            logger.info('Message broker stops listening')
            return False

        return True
