# -*- coding: utf-8 -*-
from playhouse.sqlite_ext import SqliteExtDatabase

from app.config import config


def get_database():
    db_config = config.get('DATABASE')
    return SqliteExtDatabase(**db_config)


database = get_database()
