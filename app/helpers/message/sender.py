# coding: utf-8
import json
import socket
import time

from app.config import config, logger


class Sender:
    """
    Send messages to `MessageBroker` through unix socket.

    Look at `threads.message_broker.MessageBroker.__dispatch() to see how
    messages are handled.
    """

    def __init__(self):
        pass

    @classmethod
    def send(cls, message, type_):
        message.update({
            'type': type_,
            'timestamp': time.time(),
            'signature': config.get('MESSAGE_BROKER_KEY')
        })
        host = config.get('MESSAGE_BROKER_HOST')
        port = int(config.get('MESSAGE_BROKER_PORT'))

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(json.dumps(message).encode('utf-8'))
        except ConnectionRefusedError:
            logger.error('Could not connect to socket')
            return False

        return True
