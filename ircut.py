# -*- code utf-8 -*-
import sys

from helpers.ircut import IRCutOff

if __name__ == "__main__":
    ir_cut_off = IRCutOff()
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == '--day' or arg == '-d':
            ir_cut_off.toggle(mode=IRCutOff.DAY)
        elif arg == '--night' or arg == '-n':
            ir_cut_off.toggle(mode=IRCutOff.NIGHT)
        else:
            print('Bad syntax')
    else:
        ir_cut_off.run()
