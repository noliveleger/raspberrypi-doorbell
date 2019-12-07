# coding: utf-8
from datetime import datetime
from gpiozero import Button as GPIOZeroButton, LED

from app.helpers import Singleton
from app.config import config, logger
from app.helpers.message.sender import Sender
from app.helpers.message.receiver_sound import Receiver as SoundReceiver
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
        self.__is_day = None

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

    def cron(self):
        """
        To be called by `app.threads.cron.Cron()`.
        See `CRON_TASKS` in `app.config.default.py:DefaultConfig`
        """
        self.activate_led(cron_mode=True)
        return

    def activate_led(self, cron_mode=False):
        if self._led_always_on:
            if cron_mode is not True:
                logger.debug('LED should be always on, turn it on')
                self.__led.on()
        else:
            sundial = Sundial()
            is_day = sundial.is_day()
            if self.__is_day != is_day:
                if sundial.mode == Sundial.DAY:
                    logger.info("Day mode: Turn button's LED off")
                    self.__led.off()
                else:
                    logger.info("Night mode: Turn button's LED on")
                    self.__led.on()

                self.__is_day = is_day

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
        logger.info('Button has been pressed')
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

        # Stop play doorbell wav file (if any)
        Sender.send({
            'action': SoundReceiver.STOP,
            'file': 'doorbell'
        }, SoundReceiver.TYPE)

        # Start play doorbell wav file
        Sender.send({
            'action': SoundReceiver.START,
            'file': 'doorbell'
        }, SoundReceiver.TYPE)

    def released(self):
        logger.debug('Button has been released')
        if not self._led_always_on:
            if Sundial().is_day():
                self.__led.off()
            else:
                self.__led.on()
        else:
            self.__led.on()
