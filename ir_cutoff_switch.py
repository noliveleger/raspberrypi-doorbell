# -*- code utf-8 -*-
import sys

from helpers.sundial import Sundial
from helpers.ir_cutoff import IRCutOff

if __name__ == "__main__":
    # Simple helper to trigger IR Cut-Off manually
    ir_cut_off = IRCutOff()
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == '--day' or arg == '-d':
            ir_cut_off.toggle(mode=Sundial.DAY)
        elif arg == '--night' or arg == '-n':
            ir_cut_off.toggle(mode=Sundial.NIGHT)
        else:
            print('Bad syntax')
    else:
        print('Bad syntax')
