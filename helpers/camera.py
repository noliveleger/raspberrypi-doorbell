# -*- code utf-8 -*-
import logging
import os
from io import BytesIO, BufferedReader
from subprocess import call
from tempfile import mkstemp
from threading import Thread

import requests

from helpers.config import config, logger
from helpers.telegram import Telegram


class Camera(Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            if config.get('USE_MOTION') is True:
                response = requests.get(config.get('MOTION_EYE_SNAPSHOT_URL'))
                buffered_reader = BufferedReader(BytesIO(response.content))
                logger.debug('Image retrieved from motionEye')
            else:
                _, temp_path = mkstemp()
                command = [
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
                    temp_path
                ]

                if logger.level > logging.DEBUG:
                    command.insert(1, '--quiet')

                call(command)
                buffered_reader = open(temp_path, 'rb')
                logger.debug('Image {} captured...'.format(temp_path))

            message_handler = Telegram(buffered_reader)
            message_handler.run()

            if config.get('USE_MOTION') is not True:
                os.remove(temp_path)

        except Exception as e:
            logger.error('Camera Helper: {}'.format(str(e)))
        return
