# -*- code utf-8 -*-
import time
from datetime import datetime, timedelta
from threading import Thread

from app.helpers.button import Button
from app.config import config, logger
from app.helpers.ir_cutoff import IRCutOff
from app.helpers.sundial import Sundial
from app.helpers import Singleton


class DayLightToggle(metaclass=Singleton):
    """
    Toggles devices in day mode as soon as `DAY` mode is on.
    It used `Sundial` mode to trigger the toggle.
    """
    def __init__(self):
        # `DayLightToggle` does not extend Thread like other classes because
        # it needs to run indefinitely and could not be terminate when main
        # process exits.
        # Launching the inner class `_DayLightToggle` as a `Thread` lets us
        # terminate it properly
        self.__inner = self._DayLightToggle()
        self.__thread = Thread(target=self.__inner.run)

    class _DayLightToggle:
        def __init__(self):
            self.__is_day = None
            self.stop = False

        def run(self):
            devices = [Button(), IRCutOff()]
            sundial = Sundial()
            next_check = datetime.now()

            while self.stop is False:
                now = datetime.now()
                if now > next_check:
                    is_day = sundial.is_day()
                    if self.__is_day != is_day:
                        logger.info('{} mode is activated'.format(
                            sundial.human_readable_mode
                        ))
                        for device in devices:
                            device.toggle(sundial.mode)

                        self.__is_day = is_day

                    next_check = datetime.now() + timedelta(seconds=int(
                        config.get('DAY_LIGHT_INTERVAL_CHECK', 60)))
                    logger.debug('Next day light check: {}'.format(next_check))

                # Sleep only 0.5 seconds, it helps to stop this thread quickly
                # if daemon is needed to be stopped or restarted
                time.sleep(0.5)

            return

    def start(self):
        self.__thread.start()

    def stop(self):
        """
        Terminates the thread
        """
        self.__inner.stop = True


