# coding: utf-8
import os
from datetime import datetime

from peewee import (
    Model,
    PrimaryKeyField,
    DateTimeField,
    CharField,
    BooleanField
)

from app.config import logger
from . import database, ModelMixin


class Token(Model,  ModelMixin):

    id = PrimaryKeyField
    created_date = DateTimeField(default=datetime.now)
    used = BooleanField(default=False)
    token = CharField(unique=True)

    class Meta:
        database = database

    def save(self, force_insert=False, only=None):

        if self.id is None:
            self.token = os.urandom(32).hex()

        try:
            return super().save(force_insert=force_insert, only=only)
        except Exception as e:
            logger.error("{}.save - {}".format(self.__class__.__name__, str(e)))

        return False
