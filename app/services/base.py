# -*- code utf-8 -*-
from abc import ABC, abstractmethod


class BaseService(ABC):

    @staticmethod
    @abstractmethod
    def start(**kwargs):
        pass
