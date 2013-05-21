#!/usr/bin/env python
'''
Created on Feb 24, 2012
@author: moloch
Copyright 2012 Root the Box
---------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
---------

Flag program, teams need to execute this on boxes
in order to gain points.  This code supports both
Windows and Linux.  A .exe can be generated for
ease of use on Windows boxes using py2exe and the
build_flag.py script.

'''

import os
import sys
import hashlib
import argparse
import platform
import websocket



__version__ = '0.1'
__port__    = '80'
__domain__  = 'game.rootthebox.com'
__path__    = ''


if platform.system().lower() in ['linux', 'darwin']:

    # === Text Colors ===
    W = "\033[0m"     # default/white
    BLA = "\033[30m"  # black
    R = "\033[31m"    # red
    G = "\033[32m"    # green
    O = "\033[33m"    # orange
    BLU = "\033[34m"  # blue
    P = "\033[35m"    # purple
    C = "\033[36m"    # cyan
    GR = "\033[37m"   # gray

    # === Styles ===
    bold = "\033[1m"

else:

    # === Text Colors ===
    W = ""
    BLA = ""
    R = ""
    G = ""
    O = ""
    BLU = ""
    P = ""
    C = ""
    GR = ""

    # === Styles ===
    bold = ""

# === Macros ===
INFO = bold + C + "[*] " + W
WARN = bold + R + "[!] " + W
PROMPT = bold + P + "[?] " + W

# Messages
BOX_OKAY = 'box ok'
TEAM_OKAY = 'team ok'
AUTH_FAIL = 'auth fail'
XID = 'xid'


def on_open(ws):
    sys.stdout.write(INFO + "Connecting to command & control ...")
    sys.stdout.flush()

def on_message(ws, message):
    if message == AUTH_OKAY:
        sys.stdout.write('\r' + INFO + "Successfully connected to command & control\n")
        sys.stdout.flush()
    elif message == BOX_OKAY:
        sys.stdout.write('\r' + INFO + "Sending team uuid, please wait ...")
        sys.stdout.flush()
        ws.send(ws.team_uuid)
    elif message == AUTH_FAIL:
        sys.stdout.write('\r' + WARN + " Command & control rejected connection\n")
        sys.stdout.flush()
        ws.close()   
    elif message.startswith(XID):
        message = message[len(XID):]
        sys.stdout.write(INFO + "Recv xid: %s\n" % str(message))
        sha = hashlib.sha256()
        sha.update(message)
        ws.send(sha.hexdigest())

def on_error(ws, error):
    sys.stderr.write(WARN + "Error: %s\n" % str(error))

def on_close(ws):
    sys.stdout.write(WARN + "Disconnected from command & control\n")


def main(domain, port, uuid, verbose=False):
    try:
        websocket.enableTrace(verbose)
        ws = websocket.WebSocketApp("ws://%s:%s/%s" % (domain, port, __path__),
            on_message = on_message,
            on_error = on_error,
            on_close = on_close,
        )
        ws.team_uuid = uuid
        ws.on_open = on_open
        ws.run_forever()
    except KeyboardInterrupt:
        sys.stdout.write('\r' + WARN + "User exit")
        os._exit(0)
    except Exception as error:
        sys.stderr.write(WARN + "Exception: %s\n" % str(error))
        os._exit(1)


##############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Root the Box: Botnet',
    )
    parser.add_argument('--version',
        action='version',
        version='%(prog)s v'+__version__
    )
    parser.add_argument('--verbose',
        help='display verbose output (default: false)',
        action='store_true',
        dest='verbose',
    )
    parser.add_argument('--domain', '-d',
        help='scoring engine ip address, or domain (default: %s)' % __domain__,
        default=__domain__,
        dest='domain',
    )
    parser.add_argument('--port', '-p',
        help='netork port to connect to (default: %s)' % __port__,
        default=__port__,
        dest='port',
    )
    parser.add_argument('--uuid', '-u',
        help='your team\'s uuid (required)' % __port__,
        required=True,
        dest='uuid',
    )
    args = parser.parse_args()
    main(args.domain, args.port, args.uuid args.verbose)