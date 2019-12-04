# -*- code utf-8 -*-
import os

from app.config import config
from app.models.process import Process
from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'sound'

    @classmethod
    def read(cls, message, last_time_received):
        if message['action'] == cls.START:
            process = Process()
            process.run([
                'aplay',
                cls.__get_file_path(message['file'])
            ], slug=message['file'])
        elif message['action'] == cls.STOP:
            Process.kill(slug=message['file'])
        else:
            return False

        return True

    @classmethod
    def __get_file_path(cls, file):
        return os.path.join(
            config.ROOT_PATH,
            'sounds',
            '{}.wav'.format(file)
        )
