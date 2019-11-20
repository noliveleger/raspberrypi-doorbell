# -*- code utf-8 -*-
import datetime
from threading import Thread

import telegram

from app.config import config, logger


bot = telegram.Bot(token=config.get('TELEGRAM_TOKEN'))


class Notification(Thread):
    """
    Sends notification through Telegram
    """
    def __init__(self, picture=None, front_door=True):
        """
        :param picture (BufferedReader)
        :param front_door (bool)
        """
        super().__init__()
        self.__picture = picture
        self.__front_door = front_door

    def run(self):
        now = datetime.datetime.now().replace(microsecond=0).isoformat()
        if self.__picture is None:
            message = config.get('NOTIFICATION_FRONT_DOOR_MESSAGE') if self.__front_door \
                else config.get('NOTIFICATION_BACK_DOOR_MESSAGE')

            bot.send_message(chat_id=config.get('TELEGRAM_CHAT_ID'),
                             text='[{}] - {}'.format(now, message))
            logger.info('Ring notification sent to Telegram')

            return  # Close thread

        try:
            bot.send_photo(chat_id=config.get('TELEGRAM_CHAT_ID'),
                           photo=self.__picture,
                           caption='[{}] - Photo'.format(now),
                           disable_notification=True)
            logger.info('Photo sent to Telegram')
        except Exception as e:
            logger.error('Could not send attachment to Telegram: {}'.format(str(e)))

        return  # Close thread
