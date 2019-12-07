# coding: utf-8
import time
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Thread

from werkzeug.utils import import_string

from app.config import config, logger
from app.helpers import Singleton


class Cron(metaclass=Singleton):
    """
    Cron service. Runs tasks every X second.
    """
    def __init__(self):

        self.__inner = self._Cron()
        self.__thread = Thread(target=self.__inner.run)

    class _Cron:
        def __init__(self):
            self.stop = False

        def run(self):
            tasks = config.get('CRON_TASKS')
            next_check = defaultdict(datetime.now)
            # Import classes only once
            classes = {class_: import_string(class_) for class_, _ in tasks}
            while self.stop is False:
                for class_, interval_check in tasks:
                    if datetime.now() > next_check[class_]:
                        obj = classes[class_]()
                        thread_ = Thread(target=obj.cron)
                        thread_.start()

                        next_check[class_] = datetime.now() \
                            + timedelta(seconds=interval_check)
                        logger.debug('Next {} check: {}'.format(
                            class_,
                            next_check[class_]))

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


