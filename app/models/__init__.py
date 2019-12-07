# coding: utf-8
from playhouse.sqlite_ext import SqliteExtDatabase

from app.config import config


def get_database():
    db_config = config.get('DATABASE')
    return SqliteExtDatabase(**db_config)


def get_models():
    from .call import Call
    from .process import Process
    from .token import Token
    return Call, Process, Token


class ModelMixin:

    def refresh_from_db(self):
        """
        https://github.com/coleifer/peewee/issues/686#issuecomment-254761341
        """
        refreshed_self = type(self).get(self._pk_expr())
        for field_name in self._meta.fields.keys():
            val = getattr(refreshed_self, field_name)
            setattr(self, field_name, val)
        self._dirty.clear()


database = get_database()
