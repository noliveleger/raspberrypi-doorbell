# -*- code utf-8 -*-
import click
from flask.cli import AppGroup

from app.helpers.sundial import Sundial
from app.services.back_doorbell_emitter import BackDoorbellEmitter
from app.services.daemon import Daemon
from app.services.ir_cutoff_switch import IRCutOffSwitch


class ServicesLoader:

    def __init__(self, app):

        services = AppGroup('services')

        @services.command('daemon')
        def daemon_():
            Daemon.start()

        @services.command('back-doorbell-emitter')
        def back_doorbell_emitter_():
            BackDoorbellEmitter.start()

        @services.command('ir-cutoff')
        @click.option('-m', '--mode',
                      type=click.Choice(['day', 'night'], case_sensitive=False))
        def ir_cutoff(mode):
            sundial_mode = Sundial.DAY if mode == 'day' else Sundial.NIGHT
            IRCutOffSwitch.start(mode=sundial_mode)

        app.cli.add_command(services)
