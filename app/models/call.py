# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from peewee import (
    Model,
    PrimaryKeyField,
    CharField,
    DateTimeField,
    IntegerField,
    DoesNotExist
)

from app.config import config, logger
from app.helpers.message.sender import Sender
from app.helpers.message.receiver_motion import Receiver as MotionReceiver
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

    def cron(self):
        """
        To be called by `app.threads.cron.Cron()`.
        See `CRON_TASKS` in `app.config.default.py:DefaultConfig`
        """
        call_heartbeat_interval = config.get('WEBRTC_CALL_HEARTBEAT_INTERVAL')
        date_ = datetime.now() - timedelta(seconds=call_heartbeat_interval * 2)

        if Call.select().where(Call.status == Call.ON_CALL,
                               Call.modified_date < date_).exists():
            logger.debug("Dead calls have been found")
            self.hang_up()

        return

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

    @classmethod
    def hang_up(cls):
        q = Call.update({Call.status: cls.HANG_UP}). \
            where(Call.status == cls.ON_CALL)
        q.execute()
        # Start motion if needed
        Sender.send({'action': MotionReceiver.START}, MotionReceiver.TYPE)

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
