# -*- code utf-8 -*-
import pytz
from datetime import date, datetime, timedelta

from astral import Astral

from helpers.config import config, logger


class Sundial:

    DAY = 1
    NIGHT = 2

    def __init__(self):
        city_name = config.get('ASTRA_CITY')
        a = Astral()
        a.solar_depression = 'civil'

        city = a[city_name]
        self.__sun = city.sun(date=date.today(), local=True)
        self.__timezone = pytz.timezone(city.timezone)

        logger.debug('Dawn:    %s' % str(self.__sun['dawn']))
        logger.debug('Sunrise: %s' % str(self.__sun['sunrise']))
        logger.debug('Sunset:  %s' % str(self.__sun['sunset']))
        logger.debug('Dusk:    %s' % str(self.__sun['dusk']))

    def is_day(self, delta=None):

        datetime_check = datetime.now(tz=self.__timezone)
        beginning_of_day = self.__sun['sunrise'] + timedelta(minutes=int(config.get('DAY_LIGHT_OFFSET')))
        end_of_day = self.__sun['sunset'] - timedelta(minutes=int(config.get('DAY_LIGHT_OFFSET')))

        if delta:
            datetime_check = datetime_check - delta

        return beginning_of_day <= datetime_check < end_of_day

    def get_sun(self):
        return self.__sun


