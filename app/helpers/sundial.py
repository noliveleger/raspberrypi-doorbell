# -*- code utf-8 -*-
import pytz
from datetime import date, datetime, timedelta

from astral import Astral

from app.config import config, logger
from app.helpers import Singleton


class Sundial(metaclass=Singleton):
    """
    Calculates sunrise/sunset schedule.

    Because there is not enough light when the sun rises (or almost sets),
    it considers it is `DAY` when time of the day is between sunrise + offset
    and sunset - offset.
    Offset can be configured in the `config.ini`. See `DAY_LIGHT_OFFSET`
    """

    DAY = 1
    NIGHT = 2

    def __init__(self):
        city_name = config.get('ASTRA_CITY')
        a = Astral()
        a.solar_depression = 'civil'

        self.__city = a[city_name]
        self.__today = None
        self.__sun = None
        self.__mode = None
        self.__timezone = pytz.timezone(self.__city.timezone)
        self.is_day()

    def is_day(self, delta=None):
        if self.__today != date.today():
            # Date change, retrieve today schedule
            self.__sun = self.__city.sun(date=date.today(), local=True)
            self.__today = date.today()

            logger.debug('Dawn:    %s' % str(self.__sun['dawn']))
            logger.debug('Sunrise: %s' % str(self.__sun['sunrise']))
            logger.debug('Sunset:  %s' % str(self.__sun['sunset']))
            logger.debug('Dusk:    %s' % str(self.__sun['dusk']))

        datetime_check = datetime.now(tz=self.__timezone)
        beginning_of_day = self.__sun['sunrise'] + timedelta(minutes=int(
            config.get('DAY_LIGHT_OFFSET')))
        end_of_day = self.__sun['sunset'] - timedelta(minutes=int(
            config.get('DAY_LIGHT_OFFSET')))

        if delta:
            datetime_check = datetime_check - delta

        is_day_ = beginning_of_day <= datetime_check < end_of_day
        self.__mode = self.DAY if is_day_ else self.NIGHT
        return is_day_

    @property
    def mode(self):
        return self.__mode

    @property
    def human_readable_mode(self):
        return 'Day' if self.__mode == self.DAY else 'Night'

    @property
    def sun(self):
        return self.__sun

