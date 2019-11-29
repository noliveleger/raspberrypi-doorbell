# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from flask import request, abort
from functools import wraps

from app.config import config, logger
from app.models.token import Token


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        acct = Auth.execute()

        if acct:
            return func(*args, **kwargs)

        abort(403)

    return wrapper


class Auth:

    @staticmethod
    def execute():

        request_datetime = datetime.now() - timedelta(seconds=int(
            config.get('AUTH_DATETIME_PADDING')))

        query = Token.select().where(Token.token == request.args.get('token'),
                                     Token.created_date >= request_datetime)
        return query.exists()
