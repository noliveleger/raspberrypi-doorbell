# -*- code utf-8 -*-
import logging
from subprocess import call
from threading import Thread

from helpers.config import config, logger
from helpers.telegram import Telegram


class Camera(Thread):

    def __init__(self, picture_path):
        """

        :param picture_path (str): Absolute Path to picture to send
        """
        super().__init__()
        self.__settings = [
            config.get('FSWEBCAM_BIN'),
            '--device',
            config.get('FSWEBCAM_DEVICE', '/dev/video0'),
            '--resolution',
            config.get('FSWEBCAM_RESOLUTION', '1920x1080'),
            '--no-banner',
            '--delay',
            config.get('FSWEBCAM_DELAY', '2'),
            '--rotate',
            config.get('FSWEBCAM_ROTATE', '180'),
            '--jpeg',
            config.get('FSWEBCAM_JPG_COMP', '80'),
            picture_path
        ]

        if logger.level > logging.DEBUG:
            self.__settings.insert(1, '--quiet')

        self.__picture_path = picture_path

    def run(self):
        try:
            print(self.__settings)
            call(self.__settings)
            logger.info('Image {} captured...'.format(self.__picture_path))
            message_handler = Telegram(self.__picture_path)
            message_handler.run()
        except Exception as e:
            logger.error(e)
        return
