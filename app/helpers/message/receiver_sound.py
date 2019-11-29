# -*- code utf-8 -*-
from . import BaseReceiver


class Receiver(BaseReceiver):

    TYPE = 'sound'

    @classmethod
    def read(cls, message, last_time_received):
        pass

