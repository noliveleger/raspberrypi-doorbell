# -*- coding: utf-8 -*-
import json
import os

from flask import Blueprint, render_template, abort, session, jsonify, request

from app.helpers.auth import authenticate
from app.config import config
from app.helpers.message.sender import Sender
from app.helpers.message.receiver_motion import Receiver as MotionReceiver
from app.helpers.message.receiver_sound import Receiver as SoundReceiver
from app.helpers.session import Session
from app.models.call import Call
from app.models.token import Token


class MobileMod:

    def __init__(self, app):
        blueprint = Blueprint('mobile_bp',
                              __name__,
                              static_folder='static',
                              template_folder='templates')

        blueprint.add_url_rule('/', 'index', self.index, methods=['GET'])
        blueprint.add_url_rule('/fake-session', 'fake_session', self.fake_session,
                               methods=['GET'])
        blueprint.add_url_rule('/hang-up', 'hang_up', self.hang_up,
                               methods=['GET'])
        blueprint.add_url_rule('/pick-up', 'pick_up', self.pick_up,
                               methods=['GET'])
        blueprint.add_url_rule('/heartbeat', 'heartbeat', self.heartbeat,
                               methods=['GET'])
        blueprint.add_url_rule('/validate-session', 'validate_session',
                               self.validate_session, methods=['GET'])

        app.register_blueprint(blueprint)

        @app.errorhandler(404)
        def page_not_found(e):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'message': 'Page not found',
                    'status_code': 404}), 404

            return render_template('404.html')

        @app.errorhandler(403)
        def forbidden(e):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'message': 'Access forbidden',
                    'status_code': 403}), 403

            return render_template('403.html')

        @app.errorhandler(423)
        def locked(e):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'message': 'Somebody already picked up the phone',
                    'status_code': 423}), 423

            return render_template('423.html')

    @authenticate
    def index(self):

        caller_id = self.__get_caller_id()

        call = Call.get_call()
        if not call.get_the_line(caller_id):
            Session.clear_auth_session()
            abort(423)

        session['caller_id'] = caller_id

        # Make the doorbell's speaker rings like a phone
        #Sender.send({
        #    'action': SoundReceiver.START,
        #    'file': 'phone-ringing'
        #}, SoundReceiver.TYPE)

        Sender.send({'action': MotionReceiver.STOP}, MotionReceiver.TYPE)

        variables = {
            'anticache': os.urandom(8).hex(),
            'domain_name': config.get('WEB_APP_DOMAIN_NAME'),
            'resolution': config.get('WEBCAM_RESOLUTION'),
            'rotate': config.get('WEBCAM_ROTATE'),
            'webrtc_web_sockets_port': config.get('WEBRTC_WEBSOCKETS_PORT'),
            'webrtc_endpoint': config.get('WEBRTC_ENDPOINT'),
            'webrtc_ice_servers': json.dumps(config.get('WEBRTC_ICE_SERVERS')),
            'webrtc_video_format': config.get('WEBRTC_VIDEO_FORMAT'),
            'webrtc_force_hw_vcodec': 'true' if config.get('WEBRTC_FORCE_HW_VCODEC') else 'false',
            'webrtc_call_heartbeat': config.get('WEBRTC_CALL_HEARTBEAT_INTERVAL')
        }

        return render_template('index.html', **variables)

    def fake_session(self):
        if config.env == 'dev':
            token = Token()
            token.save()

            url = 'https://{domain}:{port}?token={token}'.format(
                domain=config.get('WEB_APP_DOMAIN_NAME'),
                port=config.get('WEB_APP_PORT'),
                token=token.token
            )

            return url
        else:
            abort(404)

    @authenticate
    def hang_up(self):
        call = self.__get_call()
        call.hang_up()

        # Clear auth session
        Session.clear_auth_session()
        return jsonify({'status': 'ok'})

    @authenticate
    def heartbeat(self):
        call = self.__get_call()
        call.save()  # For Garbage collector
        return jsonify({'status': 'ok'})

    @authenticate
    def pick_up(self):
        # Make the doorbell's speaker stop ringing
        Sender.send({
            'action': SoundReceiver.STOP,
            'file': 'phone-ringing'
        }, SoundReceiver.TYPE)
        return jsonify({'status': 'ok'})

    @authenticate
    def validate_session(self):
        return jsonify({'status': 'ok'})

    def __get_call(self):

        call = Call.get_call()

        if call.caller_id != self.__get_caller_id():
            abort(403)

        return call

    @staticmethod
    def __get_caller_id():
        return session.get('caller_id', os.urandom(32).hex())
