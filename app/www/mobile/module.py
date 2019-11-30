# -*- coding: utf-8 -*-
import json

from flask import Blueprint, render_template, abort

# from app.helpers.auth import authenticate
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

        app.register_blueprint(blueprint)

    # @authenticate
    def index(self):
        # Make the doorbell's speaker rings like a phone
        Sender.send({
            'action': SoundReceiver.START,
            'file': 'phone-ringing'
        }, SoundReceiver.TYPE)

        call = Call.get_call()
        if call.is_busy:
            abort(423)

        Call.create(status=Call.ON_CALL)
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

    def hang_up(self):
        call = Call.get_call()
        if not call.is_busy:
            abort(410)
        call.hang_up()
        # Restart motion on hang up
        Sender.send({'action': MotionReceiver.START}, MotionReceiver.TYPE)

        return 'hang_up'

    def pick_up(self):
        # Make the doorbell's speaker stop ringing
        Sender.send({
            'action': SoundReceiver.STOP,
            'file': 'phone-ringing'
        }, SoundReceiver.TYPE)
        return 'pick_up'

