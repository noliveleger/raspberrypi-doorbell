# -*- code utf-8 -*-
from datetime import datetime
from gpiozero import Button as GPIOZeroButton, LED

from app.helpers import Singleton
from app.config import config, logger
from app.helpers.sundial import Sundial
from app.threads.camera import Camera
from app.threads.chime import Chime
from app.threads.notification import Notification


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

        self.__button.when_pressed = self.pressed
        self.__button.when_released = self.released
        self._led_always_on = config.get('BUTTON_LED_ALWAYS_ON')  # Protected to access from unit tests
        if self._led_always_on:
            logger.debug('LED should be always on, turn it on')
            self.__led.on()

    def __del__(self):
        if self.__button:
            self.__button.close()
            logger.debug("Button's GPIO is closed")

        if self.__led:
            self.__led.close()
            logger.debug("LED's GPIO is closed")

    @property
    def button(self):
        return self.__button

    @property
    def last_pressed(self):
        return self.__last_pressed

    @property
    def led(self):
        return self.__led

    @property
    def led_always_on(self):
        return self._led_always_on

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

        if not self._led_always_on:
            if Sundial().is_day():
                self.__led.on()
            else:
                self.__led.off()
        else:
            self.__led.off()

    def released(self):
        logger.debug('Button is released...')
        if not self._led_always_on:
            if Sundial().is_day():
                self.__led.off()
            else:
                self.__led.on()
        else:
            self.__led.on()

    def toggle(self, mode):
        if not self._led_always_on:
            if mode == Sundial.DAY:
                logger.warning("Day mode: Turn button's LED off")
                self.__led.off()
            else:
                logger.warning("Night mode: Turn button's LED on")
                self.__led.on()
