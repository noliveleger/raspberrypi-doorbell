# -*- code utf-8 -*-
from datetime import datetime
from tempfile import mkstemp
from signal import pause

from gpiozero import LED, Button

from helpers.bell import Bell
from helpers.camera import Camera
from helpers.config import config, logger
from helpers.ircut import IRCutOff
from helpers.telegram import Telegram


led = LED(config.get('LED_GPIO'))
button = Button(config.get('BUTTON_GPIO'))
last_pressed = datetime.now()


def button_pressed():
    global last_pressed
    file_id, temp_path = mkstemp()
    logger.info('Button is pressed...')
    delta = datetime.now() - last_pressed
    if delta.seconds >= int(config.get('BUTTON_PRESS_THRESHOLD')):
        logger.debug('Button has been pressed')
        bell = Bell()
        bell.start()
        camera = Camera(temp_path)
        camera.start()
        message_handler = Telegram()
        message_handler.start()
        last_pressed = datetime.now()
    else:
        logger.debug('Button was pressed too quickly!')

    led.off()


def button_released():
    logger.debug("Button is released...")
    led.on()


led.on()
ir_cut_off = IRCutOff(force=True)
ir_cut_off.start()
button.when_pressed = button_pressed
button.when_released = button_released

logger.info('Daemon is started!')

try:
    pause()
except (SystemExit, KeyboardInterrupt):
    pass

logger.debug('Cleaning up...')
led.close()
button.close()
logger.info('Daemon has been stop')
