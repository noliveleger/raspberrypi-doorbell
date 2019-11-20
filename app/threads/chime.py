# -*- code utf-8 -*-
from threading import Thread
from time import sleep

from gpiozero import Buzzer

from app.config import config, logger


class Chime(Thread):
    """
    Makes the doorbell chime rings.
    - Front door: Default (once)
    - Back door: Configurable in `config.ini`. See `BACK_DOORBELL_RINGS_NUMBER`
    """
    def __init__(self, times=1):
        """
        Makes the bell chimes
        :param times: number of times the bell must chime
        """
        self.__times = int(times)
        self.__buzzer = Buzzer(config.get('CHIME_GPIO_BCM'))
        super().__init__()

    def __del__(self):
        if self.__buzzer:
            self.__buzzer.close()

    def run(self):
        try:
            logger.debug('Ring bell, ring bell...')
            for i in range(0, self.__times):
                self.__buzzer.on()
                sleep(0.4)
                self.__buzzer.off()
                sleep(0.4)
        except Exception as e:
            logger.error(e)

        return  # Close thread

