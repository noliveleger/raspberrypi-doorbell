# -*- code utf-8 -*-
from signal import pause

from helpers.config import logger
from helpers.message import Message
from helpers.button import Button
from threads.day_light_toggle import DayLightToggle
from threads.message_broker import MessageBroker

if __name__ == "__main__":
    # Init button & leds
    button = Button()

    # Start Day Light
    day_light_toggle = DayLightToggle()
    day_light_toggle.start()

    # Listen for messages through socket (e.g. Amazon Dash Button/Back Door)
    MessageBroker = MessageBroker()
    MessageBroker.start()

    logger.info('Daemon is started!')

    try:
        pause()
    except (SystemExit, KeyboardInterrupt):
        pass

    logger.debug('Cleaning up...')
    Message.send_signal(Message.SIGNAL_STOP)
    logger.info('Daemon has been stopped')
