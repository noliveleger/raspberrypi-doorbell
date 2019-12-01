# -*- coding: utf-8 -*-
import json
import os

from flask import Blueprint, render_template, abort, session, jsonify

from app.helpers.auth import authenticate
from app.config import config
from app.helpers.message.sender import Sender
from app.helpers.message.receiver_motion import Receiver as MotionReceiver
from app.helpers.message.receiver_sound import Receiver as SoundReceiver
from app.models.call import Call


class MobileMod:

    def __init__(self, app):
        blueprint = Blueprint('mobile_bp',
                              __name__,
                              static_folder='static',
                              template_folder='templates')

        blueprint.add_url_rule('/', 'index', self.index, methods=['GET'])
        blueprint.add_url_rule('/hang_up', 'hang_up', self.hang_up, methods=['GET'])
        blueprint.add_url_rule('/pick_up', 'pick_up', self.pick_up, methods=['GET'])
        blueprint.add_url_rule('/heartbeat', 'heartbeat', self.heartbeat, methods=['GET'])

        app.register_blueprint(blueprint)

    @authenticate
    def index(self):

        caller_id = self.__get_caller_id()

        call = Call.get_call()
        if not call.get_the_line(caller_id):
            session.pop('authenticate', None)
            abort(423)

        session['caller_id'] = caller_id

        # Make the doorbell's speaker rings like a phone
        Sender.send({
            'action': SoundReceiver.START,
            'file': 'phone-ringing'
        }, SoundReceiver.TYPE)

        Sender.send({'action': MotionReceiver.STOP}, MotionReceiver.TYPE)

        variables = {
            'domain_name': config.get('WEB_APP_DOMAIN_NAME'),
            'resolution': config.get('WEBCAM_RESOLUTION'),
            'rotate': config.get('WEBCAM_ROTATE'),
            'webrtc_web_sockets_port': config.get('WEBRTC_WEBSOCKETS_PORT'),
            'webrtc_endpoint': config.get('WEBRTC_ENDPOINT'),
            'webrtc_ice_servers': json.dumps(config.get('WEBRTC_ICE_SERVERS')),
            'webrtc_video_format': config.get('WEBRTC_VIDEO_FORMAT'),
            'webrtc_force_hw_vcodec': 'true' if config.get('WEBRTC_FORCE_HW_VCODEC') else 'false'
        }

        return render_template('index.html', **variables)

    @authenticate
    def hang_up(self):
        call = self.__get_call()
        call.hang_up()

        # Clear auth session
        session.pop('authenticate', None)

        # Restart motion
        Sender.send({'action': MotionReceiver.START}, MotionReceiver.TYPE)
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

    def __get_call(self):

        call = Call.get_call()

        if call.caller_id != self.__get_caller_id():
            abort(403)

        return call

    @staticmethod
    def __get_caller_id():
        return session.get('caller_id', os.urandom(32).hex())
