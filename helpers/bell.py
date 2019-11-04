# -*- code utf-8 -*-
from threading import Thread
from time import sleep

from gpiozero import Buzzer

from helpers.config import config, logger


class Bell(Thread):

    def __init__(self, times=1):
        """
        Makes the bell rings
        :param times: number of times, the bell must rings
        """
        self.__times = times
        super().__init__()

    def run(self):
        try:
            logger.debug('Ring bell, ring bell...')
            bz = Buzzer(config.get('BELL_GPIO_BCM'))
            for i in range(0, self.__times):
                bz.on()
                sleep(0.4)
                bz.off()
                sleep(0.4)
            bz.close()
        except Exception as e:
            logger.error(e)
        return
