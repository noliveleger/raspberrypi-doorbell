# -*- code utf-8 -*-
from threading import Thread
from time import sleep

from gpiozero import Buzzer

from helpers.config import config, logger


class Bell(Thread):

    def __init__(self):
        """
        """
        super().__init__()

    def run(self):
        try:
            logger.debug('Ring bell, ring bell...')
            bz = Buzzer(config.get('BELL_GPIO'))
            bz.on()
            sleep(0.4)
            bz.off()
            sleep(0.4)
            bz.close()
        except Exception as e:
            logger.error(e)
        return
