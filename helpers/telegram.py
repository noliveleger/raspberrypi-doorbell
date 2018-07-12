# -*- code utf-8 -*-
import os
from threading import Thread

import telegram

from helpers.config import config, logger

bot = telegram.Bot(token=config.get('TELEGRAM_TOKEN'))


class Telegram(Thread):

    def __init__(self, picture_path=None):
        """

        :param picture_path (str): Absolute Path to picture to send
        """
        super().__init__()
        self.__picture_path = picture_path

    def run(self):

        if self.__picture_path is None:
            bot.send_message(chat_id=config.get('TELEGRAM_CHAT_ID'),
                             text="Ça sonne à la porte!")
            logger.info('Ring notification sent to Telegram')
        elif os.path.isfile(self.__picture_path):
            attachment = open(self.__picture_path, 'rb')
            bot.send_photo(chat_id=config.get('TELEGRAM_CHAT_ID'),
                           photo=attachment,
                           caption="Photo",
                           disable_notification=True)
            logger.info('Photo sent to Telegram')
            os.remove(self.__picture_path)
            logger.info('Photo deleted from disk')
        else:
            logger.error('{} does not exist!'.format(self.__picture_path))

        return  # Close thread
