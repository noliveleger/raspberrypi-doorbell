# -*- code utf-8 -*-
from helpers.config import config
from helpers.message import Message

if __name__ == "__main__":
    message = {'device': config.get('BACK_DOORBELL_DEVICE_MAC')}
    Message.send_message(message, Message.TYPE_CHIME)
