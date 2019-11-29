# -*- code utf-8 -*-
import subprocess

from app.config import config, logger
from app.threads.day_light_toggle import DayLightToggle

from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'motion'

    @classmethod
    def read(cls, message, last_time_received):
        if message['action'] == cls.START:
            if config.get('USE_MOTION') is True:
                cls.__run_command([
                    'sudo',
                    'systemctl',
                    'restart',
                    'motioneye'
                ])
        elif message['action'] == cls.STOP:
            if config.get('USE_MOTION') is True:
                cls.__run_command([
                    'sudo',
                    'systemctl',
                    'stop',
                    'motioneye'
                ])
        else:
            return False

        return True

    @staticmethod
    def __run_command(command):
        cp = subprocess.run(command, stdout=subprocess.PIPE)
        if cp.returncode is not 0:
            logger.error('Receiver[Motion]: {}'.format(cp.stdout))
