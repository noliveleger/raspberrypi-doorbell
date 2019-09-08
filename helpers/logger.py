# -*- code utf-8 -*-
import logging


class Logger:

    @staticmethod
    def get_logger(level_str):
        logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logger = logging.getLogger()
        if level_str == 'DEBUG':
            level = logging.DEBUG
        elif level_str == 'INFO':
            level = logging.INFO
        elif level_str == 'WARNING':
            level = logging.WARNING
        else:
            level = logging.ERROR
        logger.setLevel(level)
        return logger

