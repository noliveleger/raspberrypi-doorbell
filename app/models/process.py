# coding: utf-8
import subprocess
from datetime import datetime

from peewee import (
    Model,
    PrimaryKeyField,
    CharField,
    DateTimeField,
    IntegerField,
)

from app.config import logger
from . import database, ModelMixin


class Process(Model, ModelMixin):

    id = PrimaryKeyField
    created_date = DateTimeField(default=datetime.now)
    modified_date = DateTimeField(default=datetime.now)
    pid = IntegerField(default=None)
    slug = CharField(max_length=32, null=True)
    command = CharField(max_length=255, null=True)

    class Meta:
        database = database

    def cron(self):
        """
        To be called by `app.threads.cron.Cron()`.
        See `CRON_TASKS` in `app.config.default.py:DefaultConfig`
        """
        self.kill_all()
        return

    def run(self, command, slug=None):
        logger.debug('Process.run: START ')
        logger.debug(command)
        proc = subprocess.Popen(command, stderr=subprocess.PIPE)
        try:
            command_str = ' '.join(command)
            self.pid = proc.pid
            self.slug = slug
            self.command = command_str

            if proc.returncode:
                logger.error('Process.run: Command `{}` failed: Error ({}): {}'.format(
                    command_str,
                    proc.returncode,
                    proc.stderr.read().encode()
                ))

            self.save()

        except Exception as e:
            logger.error('Process.run: Command `{}` failed: Error: {}'.format(
                command_str,
                str(e)))

        logger.debug('Process.run: END ' + command_str)

    @classmethod
    def kill(cls, slug):
        logger.debug('Process.run: KILL ' + slug)
        if slug is None:
            processes = Process.select().where(cls.slug.is_null(False))
        else:
            processes = Process.select().where(cls.slug == slug)

        for process in processes:
            cp = subprocess.run(['kill', '-9', str(process.pid)],
                                stderr=subprocess.PIPE)
            if cp.returncode != 0:
                logger.error('Process #{} ({}) could not be killed'.format(
                    process.pid,
                    process.slug
                ))
            else:
                logger.debug('Process #{} ({}) has been killed'.format(
                    process.pid,
                    process.slug
                ))

            process.delete_instance()

    @classmethod
    def kill_all(cls):
        cls.kill(slug=None)

    def save(self, force_insert=False, only=None):

        if self.id is not None:
            self.modified_date = datetime.now()

        try:
            return super().save(force_insert=force_insert, only=only)
        except Exception as e:
            logger.error("{}.save - {}".format(self.__class__.__name__, str(e)))

        return False
