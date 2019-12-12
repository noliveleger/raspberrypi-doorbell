# coding: utf-8
import datetime
from threading import Thread

import telegram

from app.config import config, logger
from app.models.token import Token


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

            if self.__front_door:
                token = Token()
                token.save()
                auth_web_app_link = 'https://{domain}:{port}?token={token}'.format(
                    message=config.get('NOTIFICATION_FRONT_DOOR_MESSAGE'),
                    domain=config.get('WEB_APP_DOMAIN_NAME'),
                    port=config.get('WEB_APP_PORT'),
                    token=token.token)
                message = '{message}\n' \
                          '[{call_cta_label}]({call_cta_link})'.\
                    format(
                        message=_('daemon/notification/front_door_message'),
                        call_cta_label=_('daemon/notification/call_cta_label'),
                        call_cta_link=auth_web_app_link)
            else:
                message = _('daemon/notification/back_door_message')

            bot.send_message(chat_id=config.get('TELEGRAM_CHAT_ID'),
                             text=message,
                             parse_mode=telegram.ParseMode.MARKDOWN)

            logger.debug('Ring notification sent to Telegram')

            return  # Close thread

        try:
            bot.send_photo(chat_id=config.get('TELEGRAM_CHAT_ID'),
                           photo=self.__picture,
                           caption=_('Photo'),
                           disable_notification=True)
            logger.debug('Photo sent to Telegram')
        except Exception as e:
            logger.error('Could not send attachment to Telegram: {}'.format(str(e)))

        return  # Close thread
