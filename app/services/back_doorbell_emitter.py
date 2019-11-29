# -*- code utf-8 -*-
from app.config import config
from app.helpers.message.sender import Sender
from app.helpers.message.receiver_chime import Receiver

from .base import BaseService


class BackDoorbellEmitter(BaseService):

    @staticmethod
    def start(**kwargs):
        message = {'device': config.get('BACK_DOORBELL_DEVICE_MAC')}
        Sender.send(message, Receiver.TYPE)
