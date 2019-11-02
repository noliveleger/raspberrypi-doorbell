# -*- code utf-8 -*-
import datetime
from threading import Thread
from time import sleep

from gpiozero import Motor

from helpers.config import config, logger
from helpers.sundial import Sundial


class IRCutOffMotor(Motor):

    def __init__(self, forward, backward, enable):
        super().__init__(forward=forward, backward=backward, enable=enable, pwm=False, pin_factory=None)

    def stop(self):
        super().stop()
        self.enable_device.off()


class IRCutOff(Thread):

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

            sundial = Sundial()

            was_day = sundial.is_day(datetime.timedelta(minutes=1))
            day = sundial.is_day()

            if was_day != day or self.__force:
                mode = Sundial.DAY if day else Sundial.NIGHT
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
        if mode == Sundial.DAY:
            logger.info('Day mode: Turn IR cut-off filter ON.')
            ir_filter.backward()
            self.__mode = Sundial.DAY
        else:
            logger.info('Night mode: Turn IR cut-off filter OFF.')
            ir_filter.forward()
            self.__mode = Sundial.NIGHT

        if config.get('TESTING'):
            return ir_filter

        sleep(0.5)
        ir_filter.stop()
        ir_filter.close()
