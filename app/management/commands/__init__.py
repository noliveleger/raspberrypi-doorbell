# -*- code utf-8 -*-
from abc import ABC, abstractmethod


class BaseCommand(ABC):

    @staticmethod
    @abstractmethod
    def start(**kwargs):
        pass
