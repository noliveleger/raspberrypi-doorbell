# -*- code utf-8 -*-
import os

import configparser

from helpers.logger import Logger


class Config:

    DEFAULT_ENV = 'default'

    def __init__(self):
        self.__config = configparser.ConfigParser()
        filename = os.path.realpath(os.path.normpath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            'config.ini'))
        )
        self.__config.read(filename)
        self.__environment = os.getenv('PYTHON_ENV', Config.DEFAULT_ENV)

        if self.__environment not in self.__config:
            raise Exception('Environment not found')

    def get(self, value, default=None):
        env = self.__environment
        if not self.__config.has_option(env, value):
            env = Config.DEFAULT_ENV

        config_value = self.__config.get(env, value, fallback=default)
        if config_value is None:
            return config_value

        if config_value.upper() == 'TRUE':
            config_value = True
        elif config_value.upper() == 'FALSE':
            config_value = False

        return config_value

    @property
    def env(self):
        return self.__environment

    @property
    def all(self):
        self.__config.items(self.__environment)


config = Config()
logger = Logger.get_logger(config.get('LOG_LEVEL'))
