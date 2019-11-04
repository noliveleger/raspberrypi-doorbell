# -*- code utf-8 -*-
import sys

from helpers.ircut import IRCutOff
from helpers.sundial import Sundial

if __name__ == "__main__":
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
        ir_cut_off.run()
