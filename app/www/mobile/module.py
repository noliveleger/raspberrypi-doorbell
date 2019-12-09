# coding: utf-8
import json
import os

from flask import (
    abort,
    Blueprint,
    jsonify,
    redirect,
    render_template,
    session,
)
from checksumdir import dirhash

from app.helpers.auth import authenticate
from app.config import config, locale
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
        blueprint.add_url_rule('/pick-up', 'pick_up', self.pick_up,
                               methods=['GET'])
        blueprint.add_url_rule('/heartbeat', 'heartbeat', self.heartbeat,
                               methods=['GET'])
        blueprint.add_url_rule('/validate-session', 'validate_session',
                               self.validate_session, methods=['GET'])
        blueprint.add_url_rule('/hang-up', 'hang_up', self.hang_up,
                               methods=['GET'])

        if config.env == 'dev':
            blueprint.add_url_rule('/call', 'call',
                                   self.call,
                                   methods=['GET'])

        app.register_blueprint(blueprint)
        self.__blueprint = blueprint

    @authenticate
    def index(self):
        """
        Check if a on-going call exists.
        If it exists, authorize access only if `caller_id` is owner's call
        If it does not exist, create the call and assign it to `caller_id`
        """
        caller_id = self.__get_caller_id()

        call = Call.get_call()
        if not call.get_the_line(caller_id):
            Session.clear_auth_session()
            abort(423)

        session['caller_id'] = caller_id

        # Make the doorbell's speaker rings like a phone
        Sender.send({
           'action': SoundReceiver.START,
           'file': 'phone-ringing'
        }, SoundReceiver.TYPE)

        Sender.send({'action': MotionReceiver.STOP}, MotionReceiver.TYPE)

        variables = {
            'anticache': dirhash(self.__blueprint.static_folder, 'sha1'),
            'domain_name': config.get('WEB_APP_DOMAIN_NAME'),
            'rotate': config.get('WEBCAM_ROTATE'),
            'webrtc_web_sockets_port': config.get('WEBRTC_WEBSOCKETS_PORT'),
            'webrtc_endpoint': config.get('WEBRTC_ENDPOINT'),
            'webrtc_ice_servers': json.dumps(config.get('WEBRTC_ICE_SERVERS')),
            'webrtc_video_format': config.get('WEBRTC_VIDEO_FORMAT'),
            'webrtc_force_hw_vcodec': 'true' if config.get('WEBRTC_FORCE_HW_VCODEC') else 'false',
            'webrtc_call_heartbeat': config.get('WEBRTC_CALL_HEARTBEAT_INTERVAL'),
            'font_awesome_id': config.get('WEB_APP_FONT_AWESOME_ID'),
            'javascript_strings': json.dumps({
                'beforeCall': _('web_app/call/before'),
                'onProgressCall':  _('web_app/call/on_progress'),
                'terminatedCall': _('web_app/call/terminated')
            })
        }

        return render_template('index.html', **variables)

    def call(self):
        """
        Simulate a notification and let us access the page with a new token.
        Useful for development. Should be NEVER accessible on production
        """
        token = Token()
        token.save()

        url = 'https://{domain}:{port}?token={token}'.format(
            domain=config.get('WEB_APP_DOMAIN_NAME'),
            port=config.get('WEB_APP_PORT'),
            token=token.token
        )

        return redirect(url, 301)

    @authenticate
    def hang_up(self):
        call = self.__get_call()
        call.hang_up()

        # Clear auth session
        Session.clear_auth_session()
        return jsonify({'status': 'ok'})

    @authenticate
    def heartbeat(self):
        """
        Update `date_modified` of `call`.
        It lets the cron job know what the call is still active
        and should not terminated
        """
        call = self.__get_call()
        call.save()
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
        """
        Only used to validate whether session is still active before
        doing some actions in JavaScript.

        @ToDo Merge with `heartbeat()`?
        """
        return jsonify({'status': 'ok'})

    def __get_call(self):

        call = Call.get_call()

        if call.caller_id != self.__get_caller_id():
            abort(403)

        return call

    @staticmethod
    def __get_caller_id():
        """
        Create a `caller_id` in case of race conditions when
        two auth sessions are created at the same time.
        Only one user can place the call.
        (e.g. 2 different users receive notifications and click the link)
        :return: str
        """
        return session.get('caller_id', os.urandom(32).hex())
