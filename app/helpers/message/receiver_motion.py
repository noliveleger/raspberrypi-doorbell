# coding: utf-8
import time

from app.config import config
from app.models.process import Process
from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'motion'

    @classmethod
    def read(cls, message, last_time_received):
        if message['action'] == cls.START:
            if config.get('USE_MOTION') is True:
                time.sleep(1)  # Give some delay to WEBRTC to release the cam
                process = Process()
                process.run([
                    'sudo',
                    'systemctl',
                    'start',
                    'motioneye'
                ])
        elif message['action'] == cls.STOP:
            if config.get('USE_MOTION') is True:
                process = Process()
                process.run([
                    'sudo',
                    'systemctl',
                    'stop',
                    'motioneye'
                ])
        else:
            return False

        return True
