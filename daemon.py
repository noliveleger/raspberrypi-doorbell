# -*- code utf-8 -*-
from datetime import datetime
from signal import pause

from gpiozero import LED, Button

from helpers.bell import Bell
from helpers.camera import Camera
from helpers.config import config, logger
from helpers.ircut import IRCutOff
from helpers.listener import BackDoorBellListener, BackDoorBellEmitter
from helpers.telegram import Telegram


led = LED(config.get('LED_GPIO_BCM'))
button = Button(config.get('BUTTON_GPIO_BCM'))
last_pressed = datetime.now()


def button_pressed():
    global last_pressed
    logger.info('Button has been pressed...')
    delta = datetime.now() - last_pressed
    if delta.seconds >= int(config.get('BUTTON_PRESS_THRESHOLD')):
        bell = Bell()
        bell.start()
        message_handler = Telegram()
        message_handler.start()
        camera = Camera()
        camera.start()
        last_pressed = datetime.now()
    else:
        logger.debug('Button was pressed too quickly!')

    led.off()


def button_released():
    logger.debug("Button is released...")
    led.on()


if __name__ == "__main__":
    # Turn front-door leds on.
    led.on()

    # Set IR-CutOff filter in position
    ir_cut_off = IRCutOff(force=True)
    ir_cut_off.start()

    # Listen for Amazon Dash Button pushes
    back_doorbell_listener = BackDoorBellListener()
    back_doorbell_listener.start()

    # Listen for button events
    button.when_pressed = button_pressed
    button.when_released = button_released

    logger.info('Daemon is started!')

    try:
        pause()
    except (SystemExit, KeyboardInterrupt):
        pass

    logger.debug('Cleaning up...')
    BackDoorBellEmitter.stop_server()
    led.close()
    button.close()
    logger.info('Daemon has been stop')
