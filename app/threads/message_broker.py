# coding: utf-8
import json
import socket
from collections import defaultdict
from datetime import datetime
from threading import Thread

from werkzeug.utils import import_string, ImportStringError

from app.config import config, logger
from app.helpers.message.receiver_message_broker import Receiver
from app.helpers.message.sender import Sender


class MessageBroker(Thread):
    """
    Broker to dispatch messages
    """
    def __init__(self):
        super().__init__()
        self.__stop = False
        self.__last_date_received = defaultdict(datetime.now)

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
            logger.error('MessageBroker: {}'.format(str(e)))
        return

    def __dispatch(self, message):
        """
        Does specific action depending on the type of `message`.

        Look at `helpers.message.receiver_*.py`

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

        try:
            class_ = 'app.helpers.message.receiver_{}.Receiver'.format(message['type'])
            receiver = import_string(class_)()
            if not receiver.read(message,
                                 self.__last_date_received[message['type']]):
                self.__stop = message.get('type') == Receiver.TYPE
                return False
            self.__last_date_received[message['type']] = datetime.fromtimestamp(
                message['timestamp'])
        except KeyError:
            logger.error('MessageBroker: Message is invalid. Some attributes are missing.')
            return False
        except ImportStringError:
            logger.error('MessageBroker: Message is invalid. Unknown receiver.')
            return False
        except Exception as e:
            logger.error('MessageBroker:Dispatch: {}'.format(str(e)))
            return False

        return True

    @staticmethod
    def stop():
        Sender.send({
            'action': Receiver.STOP
        }, Receiver.TYPE)

