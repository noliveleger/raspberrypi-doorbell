# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, abort

# from app.helpers.auth import authenticate
from app.helpers.message.sender import Sender
from app.helpers.message.receiver_motion import Receiver as MotionReceiver
from app.helpers.message.receiver_sound import Receiver as SoundReceiver
from app.models.call import Call


class MobileMod:

    def __init__(self, app):
        blueprint = Blueprint('mobile_module', __name__, template_folder='templates')

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

        return render_template('index.html')

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

