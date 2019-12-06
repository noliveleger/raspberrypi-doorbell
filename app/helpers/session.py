# -*- code utf-8 -*-
from datetime import datetime

from flask import session
from peewee import DoesNotExist

from app.models.token import Token


class Session:

    @staticmethod
    def clear_auth_session():
        success = True
        try:
            token = session['authenticate']['token']
            token_obj = Token.select().where(Token.token == token).get()
            token_obj.used = True
            token_obj.save()
        except (KeyError, DoesNotExist):
            success = False

        session.pop('authenticate', None)
        return success

    @staticmethod
    def create_auth_session(token, request_datetime):
        session['authenticate'] = {
            'request_datetime': request_datetime,
            'token': token,
            'datetime': datetime.now()
        }

    @staticmethod
    def renew_auth_session():
        session['authenticate']['datetime'] = datetime.now()

    @staticmethod
    def exists():
        try:
            return isinstance(session['authenticate'], dict)
        except KeyError:
            return False


