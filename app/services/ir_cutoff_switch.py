# -*- code utf-8 -*-
from app.helpers.ir_cutoff import IRCutOff
from .base import BaseService


class IRCutOffSwitch(BaseService):
    # Simple helper to trigger IR Cut-Off manually

    @staticmethod
    def start(**kwargs):
        ir_cut_off = IRCutOff()
        ir_cut_off.toggle(mode=kwargs.get('mode'))
