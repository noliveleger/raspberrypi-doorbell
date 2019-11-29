# -*- coding: utf-8 -*-
import os
from datetime import datetime

from peewee import (
    Model,
    PrimaryKeyField,
    DateTimeField,
    CharField,
    BooleanField,
    IntegerField,
    DoesNotExist
)

from app.config import logger
from . import database


class Call(Model):

    ON_CALL = 1
    HANG_UP = 2

    id = PrimaryKeyField
    created_date = DateTimeField(default=datetime.now)
    modified_date = DateTimeField(default=datetime.now)
    status = IntegerField(default=None)

    class Meta:
        database = database

    @classmethod
    def get_call(cls):
        try:
            call = cls.select().where(cls.status == cls.ON_CALL).get()
        except DoesNotExist:
            call = cls()

        return call

    def hang_up(self):
        self.status = self.HANG_UP
        self.save()

    @property
    def is_busy(self):
        return self.status == self.ON_CALL

    def save(self, force_insert=False, only=None):

        if self.id is not None:
            self.modified_date = datetime.now()

        try:
            return super().save(force_insert=force_insert, only=only)
        except Exception as e:
            logger.error("{}.save - {}".format(self.__class__.__name__, str(e)))

        return False
