# -*- code utf-8 -*-
import json
import socket
from datetime import datetime
from threading import Thread

from helpers.config import config, logger
from helpers.message import Message
from threads.chime import Chime
from threads.notification import Notification
from threads.day_light_toggle import DayLightToggle


class MessageBroker(Thread):
    """
    Broker to dispatch messages
    """
    def __init__(self):
        super().__init__()
        self.__stop = False
        self.__last_pressed = None

    def run(self):
        host = config.get('MESSAGE_BROKER_HOST')
        port = int(config.get('MESSAGE_BROKER_PORT'))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                s.listen()
                logger.info('Message broker is listening on {}:{}'.format(
                    host,
                    port
                ))
                self.__last_pressed = datetime.now()
                while not self.__stop:
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024)
                            try:
                                message = json.loads(data.decode('utf-8'))
                            except (ValueError, TypeError):
                                break  # Invalid message

                            logger.debug('Message received: {}'.format(message))

                            if not self.__dispatch(message):
                                break

        except Exception as e:
            logger.error(e)
        return

    def __dispatch(self, message):
        """
        Does specific action depending on the type of `message`.

        As of today, only 2 types of messages are handled:
        - `TYPE_CHIME`: To make the chime rings when Amazon Dash Button is pressed
        - `TYPE_SIGNAL`: To make the socket stop listening if signal is "stop"

        More to come.

        It returns a boolean to tell the socket whether it should continue to
        receive data or not.

        :param message: dict
        :return: boolean
        """
        # Not really useful to check the signature until socket listens on
        # 127.0.0.1
        if message.get('signature') != config.get('MESSAGE_BROKER_KEY'):
            logger.error('Invalid signature {}'.format(message.get('signature')))
            return False

        if message['type'] == Message.TYPE_CHIME:
            try:
                message_datetime = datetime.fromtimestamp(message['timestamp'])
                delta = message_datetime - self.__last_pressed
                if delta.seconds >= int(config.get('BUTTON_PRESS_THRESHOLD')):
                    self.__last_pressed = message_datetime
                    if message.get('device') == config.get('BACK_DOORBELL_DEVICE_MAC'):
                        telegram = Notification(front_door=False)
                        telegram.start()
                        chime = Chime(times=config.get('BACK_DOORBELL_RINGS_NUMBER'))
                        chime.run()  # No need to run it as thread
                else:
                    logger.debug('Relax dude! Stop pushing the button')
            except KeyError:
                logger.error('Message is invalid.')
                return False

        elif message['type'] == Message.TYPE_MESSAGE:
            pass

        elif message['type'] == Message.TYPE_SIGNAL:

            if message['signal'] == Message.SIGNAL_STOP:
                # Stop `DayLightToggle`'s inner thread
                day_light_toggle = DayLightToggle()
                day_light_toggle.stop()

                # stop server and its thread. Must be the last thing to stop
                self.__stop = True
                logger.warning('Message broker stops listening')
                return False

        return True


