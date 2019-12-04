# -*- code utf-8 -*-
from app.devices.ir_cut_off import IRCutOff
from . import BaseCommand


class IRCutOffSwitch(BaseCommand):
    # Simple helper to trigger IR Cut-Off manually

    @staticmethod
    def start(**kwargs):
        ir_cut_off = IRCutOff()
        ir_cut_off.toggle(mode=kwargs.get('mode'))
