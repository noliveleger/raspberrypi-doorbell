# coding: utf-8
from datetime import datetime

from app.config import config, logger
from app.threads.chime import Chime
from app.threads.notification import Notification
from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'chime'

    @classmethod
    def read(cls, message, last_time_received):
        try:
            message_datetime = datetime.fromtimestamp(message['timestamp'])
            delta = message_datetime - last_time_received
            if delta.seconds >= int(config.get('BUTTON_PRESS_THRESHOLD')):
                if message.get('device') == config.get('BACK_DOORBELL_DEVICE_MAC'):
                    telegram = Notification(front_door=False)
                    telegram.start()
                    chime = Chime(times=config.get('BACK_DOORBELL_RINGS_NUMBER'))
                    chime.run()  # No need to run it as thread
            else:
                logger.debug('Relax dude! Stop pushing the button')
        except KeyError:
            logger.error('Message is invalid.')
            return False

