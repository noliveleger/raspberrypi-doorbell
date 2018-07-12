# -*- code utf-8 -*-
import os

import configparser

from helpers.logger import Logger


class Config:

    def __init__(self):
        self.__config = configparser.ConfigParser()
        filename = os.path.realpath(os.path.normpath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            'config.ini'))
        )
        self.__config.read(filename)
        self.__environment = os.getenv('PYTHON_ENV', 'default')
        if self.__environment not in self.__config:
            raise Exception('Environment not found')

    def get(self, value, default=None):
        return self.__config.get(self.__environment, value, fallback=default)


config = Config()
logger = Logger.get_logger(config.get('LOG_LEVEL'))
