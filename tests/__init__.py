# coding: utf-8


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


class DummyThread:

    def run(self):
        return
