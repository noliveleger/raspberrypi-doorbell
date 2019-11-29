# -*- code utf-8 -*-
from abc import ABC, abstractmethod


class BaseReceiver(ABC):

    STOP = 'stop'
    START = 'start'

    @classmethod
    @abstractmethod
    def read(cls, message, last_time_received):
        return True
