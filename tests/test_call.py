# coding: utf-8
import time

from flask import url_for
from mock import patch

from app.config import config
from app.models.call import Call
from app.models.token import Token
from . import MockSocket


def test_non_valid_token(client):

    response = client.get(url_for('mobile_bp.index', _external=False))
    assert response.status_code == 403


@patch('socket.socket', new=MockSocket)
def test_valid_token(client):
    token = Token()
    token.save()

    # Try with querystring
    response = client.get(url_for('mobile_bp.index', token=token.token, _external=False))
    assert response.status_code == 200

    # Then session
    response = client.get(url_for('mobile_bp.index', _external=False))
    assert response.status_code == 200

    token.refresh_from_db()
    assert token.used is True
    token.delete_instance()
    call = Call.get_call()
    assert call.status == Call.ON_CALL
    call.delete_instance()


def test_expired_token(client):
    token = Token()
    token.save()

    time.sleep(config.get('AUTH_DATETIME_PADDING') + 1)
    # Try with querystring
    response = client.get(url_for('mobile_bp.index', token=token.token, _external=False))
    assert response.status_code == 403

    token.delete_instance()


def test_valid_already_taken_token(client):

    token = Token()
    token.used = True
    token.save()

    response = client.get(url_for('mobile_bp.index', token=token.token, _external=False))
    assert response.status_code == 403

    token.delete_instance()


def test_valid_token_busy_line(client):
    token = Token()
    token.save()
    dummy_caller_id = '123456789'
    call = Call()
    call.get_the_line(dummy_caller_id)

    response = client.get(url_for('mobile_bp.index', token=token.token, _external=False))
    assert response.status_code == 423

    call.delete_instance()
    token.delete_instance()


@patch('socket.socket', new=MockSocket)
def test_hang_up(client):
    token = Token()
    token.save()

    response = client.get(url_for('mobile_bp.index', token=token.token, _external=False))
    assert response.status_code == 200

    call = Call.get_call()
    assert call.status == Call.ON_CALL

    response = client.get(url_for('mobile_bp.hang_up', _external=False))
    call.refresh_from_db()
    assert response.status_code == 200
    assert call.status == Call.HUNG_UP

    response = client.get(url_for('mobile_bp.validate_session', _external=False))
    assert response.status_code == 403


@patch('socket.socket', new=MockSocket)
def test_cron(app):

    dummy_caller_id = '123456789'
    call = Call()
    call.get_the_line(dummy_caller_id)
    active_call = Call.get_call()
    assert active_call.id is not None
    assert call == active_call

    # Simulate heartbeat missed once
    time.sleep(config.get('WEBRTC_CALL_HEARTBEAT_INTERVAL'))
    Call.cron()
    active_call = Call.get_call()
    assert active_call.id is not None

    call.refresh_from_db()
    assert call.status == Call.ON_CALL

    # Simulate heartbeat missed twice
    time.sleep(config.get('WEBRTC_CALL_HEARTBEAT_INTERVAL'))
    Call.cron()
    active_call = Call.get_call()
    assert active_call.id is None

    call.refresh_from_db()
    assert call.status == Call.HUNG_UP
