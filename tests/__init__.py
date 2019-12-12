# coding: utf-8
from gpiozero import Buzzer

from app.config import config


class MockChime:

    def __init__(self, times=1):
        """
        Makes the bell chimes
        :param times: number of times the bell must chime
        """
        self.__times = int(times)
        self.__buzzer = Buzzer(config.get('CHIME_GPIO_BCM'))
        super().__init__()

    def __del__(self):
        if self.__buzzer:
            self.__buzzer.close()

    def run(self):
        for i in range(0, self.__times):
            self.__buzzer.on()
            self.__cpt += 1


class MockSocket:

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self

    def connect(self, address):
        pass

    def sendall(self, json_):
        pass

    def setsockopt(self, *args):
        pass


class MockThread:

    def run(self):
        return


