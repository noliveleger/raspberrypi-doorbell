# coding: utf-8
import functools
import threading

lock = threading.Lock()


def synchronized(lock_):
    """
    Synchronization decorator
    """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock_:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper


class Singleton(type):
    """
    Thread safe singleton metaclass
    See: https://stackoverflow.com/a/50567397 and https://stackoverflow.com/a/55629949

    Every class which inherits from Singleton cannot be called within the constructor
    of another class which inherits from Singleton too.
    Otherwise a lock will occur because of `@synchronized(lock)` decorator.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._locked_call(*args, **kwargs)
        return cls._instances[cls]

    @synchronized(lock)
    def _locked_call(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
