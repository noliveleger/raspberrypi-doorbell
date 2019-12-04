# -*- code utf-8 -*-
import click
from flask.cli import AppGroup

from app.helpers.sundial import Sundial
from app.management.commands.back_doorbell_emitter import BackDoorbellEmitter
from app.management.commands.daemon import Daemon
from app.management.commands.ir_cutoff_switch import IRCutOffSwitch


class CommandsLoader:
    """
    Adds external commands to Flask
    """
    def __init__(self, app):

        commands = AppGroup('commands', help='Management commands.')

        @commands.command('daemon')
        def daemon_():
            """
            Start daemon.
            """
            Daemon.start()

        @commands.command('back-doorbell-emitter')
        def back_doorbell_emitter_():
            """
            Emit signal to daemon to make back doorbell chimes.
            """
            BackDoorbellEmitter.start()

        @commands.command('ir-cutoff')
        @click.option('-m', '--mode',
                      type=click.Choice(['day', 'night'], case_sensitive=False))
        def ir_cutoff(mode):
            """
            Toggle IR Cut Off filter in desired mode.
            """
            sundial_mode = Sundial.DAY if mode == 'day' else Sundial.NIGHT
            IRCutOffSwitch.start(mode=sundial_mode)

        app.cli.add_command(commands)
