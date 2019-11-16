# -*- code utf-8 -*-
import json
import socket
import time

from helpers.config import config, logger


class Message:
    """
    Send messages to `MessageBroker` through unix socket.

    Look at `threads.message_broker.MessageBroker.__dispatch() to see how
    messages are handled.
    """

    TYPE_SIGNAL = 'signal'
    TYPE_MESSAGE = 'message'
    TYPE_CHIME = 'chime'
    SIGNAL_STOP = 'stop'

    def __init__(self):
        pass

    @classmethod
    def send_message(cls, message, type_=TYPE_MESSAGE):
        message.update({
            'type': type_,
            'timestamp': time.time(),
            'signature': config.get('MESSAGE_BROKER_KEY')
        })
        cls.__send_message(message)

    @classmethod
    def send_signal(cls, signal):
        message = {
            'type': cls.TYPE_SIGNAL,
            'signal': signal,
            'signature': config.get('MESSAGE_BROKER_KEY')
        }
        cls.__send_message(message)

    @staticmethod
    def __send_message(message):
        host = config.get('MESSAGE_BROKER_HOST')
        port = int(config.get('MESSAGE_BROKER_PORT'))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(message).encode('utf-8'))

