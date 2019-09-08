# -*- code utf-8 -*-
import json
import socket
import time
from datetime import datetime
from threading import Thread, Event

from helpers.bell import Bell
from helpers.config import config, logger
from helpers.telegram import Telegram


class BackDoorBellListener(Thread):

    def __init__(self):
        """
        """
        super().__init__()
        self.__stop = False

    def run(self):
        host = '127.0.0.1'
        port = int(config.get('BACK_DOORBELL_LISTENER_PORT'))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                s.listen()
                logger.info('Back door listener is up and running on {}:{}'.format(host, port))
                last_pressed = datetime.now()
                while not self.__stop:
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024)
                            try:
                                message = json.loads(data.decode('utf-8'))
                            except (ValueError, TypeError):
                                break  # Invalid message

                            logger.debug('Message: {}'.format(message))

                            if message.get('stop') == config.get('BACK_DOORBELL_KEY'):
                                # stop server and its thread
                                self.__stop = True
                                break
                            try:
                                message_datetime = datetime.fromtimestamp(message['timestamp'])
                                delta = message_datetime - last_pressed
                                if delta.seconds >= int(config.get('BUTTON_PRESS_THRESHOLD')):
                                    last_pressed = message_datetime
                                    if message.get('device') == config.get('BACK_DOORBELL_DEVICE_MAC'):
                                        telegram = Telegram(front_door=False)
                                        telegram.start()
                                        bell = Bell(times=2)
                                        bell.run()  # No need to run it as thread
                                else:
                                    logger.debug('Relax dude! Stop pushing the button')
                            except KeyError:
                                logger.error('Message is invalid.')
                                break
        except Exception as e:
            logger.error(e)
        return


class BackDoorBellEmitter:

    def __init__(self):
        pass

    @classmethod
    def send(cls):
        message = {
            'device': config.get('BACK_DOORBELL_DEVICE_MAC'),
            'timestamp': time.time()
        }
        cls.__send_message(message)

    @classmethod
    def stop_server(cls):
        message = {
            'stop': config.get('BACK_DOORBELL_KEY')
        }
        cls.__send_message(message)

    @staticmethod
    def __send_message(message):
        host = '127.0.0.1'
        port = int(config.get('BACK_DOORBELL_LISTENER_PORT'))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(message).encode('utf-8'))

