# -*- code utf-8 -*-
from app.config import config
from app.helpers.message import Message
from .base import BaseService


class BackDoorbellEmitter(BaseService):

    @staticmethod
    def start(**kwargs):
        message = {'device': config.get('BACK_DOORBELL_DEVICE_MAC')}
        Message.send_message(message, Message.TYPE_CHIME)
