# -*- coding: utf-8 -*-
from datetime import datetime

from peewee import (
    Model,
    PrimaryKeyField,
    CharField,
    DateTimeField,
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
    caller_id = CharField(max_length=32, null=True)

    class Meta:
        database = database

    @classmethod
    def get_call(cls):
        try:
            call = cls.select().where(cls.status == cls.ON_CALL). \
                order_by(cls.modified_date.desc()).get()
        except DoesNotExist:
            call = cls()

        return call

    def get_the_line(self, caller_id):
        if not self.is_line_busy:
            self.__create_call(caller_id)
        elif self.caller_id != caller_id:
            return False
        return True

    def hang_up(self):
        q = Call.update({Call.status: self.HANG_UP}). \
            where(Call.status == self.ON_CALL)
        q.execute()

    @property
    def is_line_busy(self):
        return self.status == self.ON_CALL

    def save(self, force_insert=False, only=None):

        if self.id is not None:
            self.modified_date = datetime.now()

        try:
            return super().save(force_insert=force_insert, only=only)
        except Exception as e:
            logger.error("{}.save - {}".format(self.__class__.__name__, str(e)))

        return False

    def __create_call(self, caller_id):
        self.caller_id = caller_id
        self.status = self.ON_CALL
        self.save()
