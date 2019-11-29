# -*- code utf-8 -*-
from app.config import logger
from app.threads.day_light_toggle import DayLightToggle

from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'message_broker'

    @classmethod
    def read(cls, message, last_time_received):
        if message['action'] == cls.STOP:
            # Stop `DayLightToggle`'s inner thread
            day_light_toggle = DayLightToggle()
            day_light_toggle.stop()

            # stop server and its thread. Must be the last thing to stop
            logger.warning('Message broker stops listening')
            return False

        return True
