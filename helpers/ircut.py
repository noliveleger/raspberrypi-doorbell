# -*- code utf-8 -*-
import datetime
import pytz
from threading import Thread
from time import sleep

from astral import Astral
from gpiozero import Motor

from helpers.config import config, logger


class IRCutOffMotor(Motor):

    def __init__(self, forward, backward, enable):
        super().__init__(forward=forward, backward=backward, enable=enable, pwm=False, pin_factory=None)

    def stop(self):
        super().stop()
        self.enable_device.off()


class IRCutOff(Thread):

    DAY = 1
    NIGHT = 2

    def __init__(self, force=False):
        """
        Toggle day/night mode.
        :param force: bool. If `True`, checks if filter needs to be toggled whatever the current state
        """
        super().__init__()
        self.__force = force
        self.__mode = None

    def run(self):
        try:
            city_name = config.get('IR_CUTOFF_CITY')

            a = Astral()
            a.solar_depression = 'civil'

            city = a[city_name]
            sun = city.sun(date=datetime.date.today(), local=True)

            timezone = pytz.timezone(city.timezone)
            now = datetime.datetime.now(tz=timezone)
            # logger.debug('Dawn:    %s' % str(sun['dawn']))
            # logger.debug('Sunrise: %s' % str(sun['sunrise']))
            # logger.debug('Sunset:  %s' % str(sun['sunset']))
            # logger.debug('Dusk:    %s' % str(sun['dusk']))
            beginning_of_day = sun['sunrise'] + datetime.timedelta(minutes=int(config.get('IR_CUTOFF_OFFSET')))
            end_of_day = sun['sunset'] - datetime.timedelta(minutes=int(config.get('IR_CUTOFF_OFFSET')))

            last_check = now - datetime.timedelta(minutes=1)
            was_day = beginning_of_day < last_check < end_of_day
            day = beginning_of_day < now < end_of_day

            if was_day != day or self.__force:
                mode = self.DAY if day else self.NIGHT
                self.toggle(mode)
            else:
                if day:
                    logger.debug('IR cut-off filter already in day mode. Nothing to do.')
                else:
                    logger.debug('IR cut-off filter already in night mode. Nothing to do.')
        except Exception as e:
            logger.error(e)
        return

    def toggle(self, mode):
        ir_filter = IRCutOffMotor(forward=config.get('IR_CUTOFF_FORWARD_PIN'),
                                  backward=config.get('IR_CUTOFF_BACKWARD_PIN'),
                                  enable=config.get('IR_CUTOFF_ENABLER_PIN'))
        if mode == self.DAY:
            logger.debug('Day mode: Turn IR cut-off filter ON.')
            ir_filter.backward()
            self.__mode = self.DAY
        else:
            logger.debug('Night mode: Turn IR cut-off filter OFF.')
            ir_filter.forward()
            self.__mode = self.NIGHT

        if config.get('TESTING'):
            return ir_filter

        sleep(0.5)
        ir_filter.stop()
        ir_filter.close()
