# coding: utf-8
import logging
import os
from io import BytesIO, BufferedReader
from shutil import move
from subprocess import call
from tempfile import mkstemp
from threading import Thread

import requests

from app.config import config, logger
from app.threads.notification import Notification


class Camera(Thread):
    """
    Takes a picture. If `motion` is used, it fetches a picture from API.
    Otherwise, it uses OS utilities (e.g. fswebcam, raspistill) to take the picture.
    It only supports `fswebcam` as of today (Nov 16, 2019)
    @ToDo Support raspistill
    """

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            _, temp_path = mkstemp()

            if config.get('USE_MOTION') is True:
                response = requests.get(config.get('MOTION_EYE_SNAPSHOT_URL'))
                buffered_reader = BufferedReader(BytesIO(response.content))
                logger.debug('Image retrieved from motionEye')
                with open(temp_path, 'wb') as capture:
                    capture.write(response.content)
            else:
                command = [
                    config.get('WEBCAM_BIN'),
                    '--device',
                    config.get('WEBCAM_DEVICE', '/dev/video0'),
                    '--resolution',
                    config.get('WEBCAM_RESOLUTION', '1920x1080'),
                    '--no-banner',
                    '--delay',
                    config.get('WEBCAM_DELAY', '2'),
                    '--rotate',
                    config.get('WEBCAM_ROTATE', '180'),
                    '--jpeg',
                    config.get('WEBCAM_JPG_COMP', '80'),
                    temp_path
                ]

                if logger.level > logging.DEBUG:
                    command.insert(1, '--quiet')

                call(command)
                buffered_reader = open(temp_path, 'rb')
                logger.debug('Image {} captured from webcam'.format(temp_path))

            notification = Notification(buffered_reader)
            notification.run()

            # Move picture in place as background for WebRTC call.
            destination_folder = os.path.join(
                config.ROOT_PATH,
                'app',
                'www',
                'mobile',
                'static',
                'img'
            )
            # Create destination folder if it does not exist
            if not os.path.exists(destination_folder):
                os.mkdir(destination_folder)

            destination = os.path.join(
                destination_folder,
                'capture.jpg'
            )
            move(temp_path, destination)

        except Exception as e:
            logger.error('Camera Helper: {}'.format(str(e)))

        return
