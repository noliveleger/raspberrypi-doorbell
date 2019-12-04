# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from flask import request, abort, session
from functools import wraps

from app.config import config
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

        if config.env != 'dev':
            return True
        else:
            try:
                auth_session = session['authenticate']
                request_datetime = auth_session['request_datetime']
                token = auth_session['token']
            except KeyError:
                request_datetime = datetime.now() - timedelta(weeks=int(
                    config.get('AUTH_DATETIME_PADDING')))
                token = request.args.get('token')

            query = Token.select().where(Token.token == token,
                                         Token.token.is_null(False),
                                         Token.created_date >= request_datetime)

            if not query.exists():
                # Not valid, don't go further
                return False

            session['authenticate'] = {
                'request_datetime': request_datetime,
                'token': token,
                'datetime': datetime.now()
            }
            return True
