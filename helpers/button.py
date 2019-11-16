# -*- code utf-8 -*-
from datetime import datetime
from gpiozero import Button as GPIOZeroButton, LED

from helpers import Singleton
from helpers.config import config, logger
from threads.camera import Camera
from threads.chime import Chime
from threads.notification import Notification


class Button(metaclass=Singleton):
    """
    Handles button events and its LEDs.
    The class is a singleton because it can be instantiated from different places
    and we need to ensure that `__button` and `__led` are still the same objects
    until daemon is running.
    """
    def __init__(self):
        self.__last_pressed = datetime.now()
        self.__button = GPIOZeroButton(config.get('BUTTON_GPIO_BCM'))
        self.__led = LED(config.get('LED_GPIO_BCM'))

        self.__led.on()
        self.__button.when_pressed = self.pressed
        self.__button.when_released = self.released

    def __del__(self):
        if self.__button:
            self.__button.close()
        if self.__led:
            self.__led.close()

    @property
    def button(self):
        return self.__button

    @property
    def last_pressed(self):
        return self.__last_pressed

    @property
    def led(self):
        return self.__led

    def pressed(self):
        logger.info('Button has been pressed...')
        delta = datetime.now() - self.__last_pressed
        if delta.seconds >= int(config.get('BUTTON_PRESS_THRESHOLD')):
            chime = Chime()
            chime.start()
            notification = Notification()
            notification.start()
            camera = Camera()
            camera.start()
            self.__last_pressed = datetime.now()
        else:
            logger.debug('Button was pressed too quickly!')

        self.__led.off()

    def released(self):
        logger.debug('Button is released...')
        self.__led.on()

    def toggle(self, mode):
        pass
