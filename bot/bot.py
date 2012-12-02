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
import re
import sys
import time
import socket
import random
import urllib
import httplib
import platform
import urlparse
import asyncore

from hashlib import sha256


SERVER = '192.168.1.143'
SERVER_PORT = '8888'

_IPV4_RE = re.compile(r'\.\d+$')
_PATH_SEP = re.compile(r'/+')

class WebSocket(object):

    def __init__(self, url, **kwargs):
        self.host, self.port, self.resource, self.secure = WebSocket._parse_url(url)
        self.protocol = kwargs.pop('protocol', None)
        self.cookie_jar = kwargs.pop('cookie_jar', None)
        self.onopen = kwargs.pop('onopen', None)
        self.onmessage = kwargs.pop('onmessage', None)
        self.onerror = kwargs.pop('onerror', None)
        self.onclose = kwargs.pop('onclose', None)
        if kwargs:
            raise ValueError('Unexpected argument(s): %s' % ', '.join(kwargs.values()))
        self._dispatcher = _Dispatcher(self)

    def send(self, data):
        self._dispatcher.write('\x00' + _utf8(data) + '\xFF')

    def close(self):
        self._dispatcher.handle_close()

    @classmethod
    def _parse_url(cls, url):
        p = urlparse.urlparse(url)

        if p.hostname:
            host = p.hostname
        else:
            raise ValueError('URL must be absolute')

        if p.fragment:
            raise ValueError('URL must not contain a fragment component')

        if p.scheme == 'ws':
            secure = False
            port = p.port or 80
        elif p.scheme == 'wss':
            raise NotImplementedError('Secure WebSocket not yet supported')
            # secure = True
            # port = p.port or 443
        else:
            raise ValueError('Invalid URL scheme')

        resource = p.path or u'/'
        if p.query: resource += u'?' + p.query
        return (host, port, resource, secure)


class WebSocketError(Exception):

    def _init_(self, value):
        self.value = value

    def _str_(self):
        return str(self.value)


class _Dispatcher(asyncore.dispatcher):

    def __init__(self, ws):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((ws.host, ws.port))

        self.ws = ws
        self._read_buffer = ''
        self._write_buffer = ''
        self._handshake_complete = False

        if self.ws.port != 80:
            hostport = '%s:%d' % (self.ws.host, self.ws.port)
        else:
            hostport = self.ws.host

        fields = [
            'Upgrade: WebSocket',
            'Connection: Upgrade',
            'Host: ' + hostport,
            'Origin: http://' + hostport,
        ]
        if self.ws.protocol:
            fields['Sec-WebSocket-Protocol'] = self.ws.protocol
        if self.ws.cookie_jar:
            cookies = filter(lambda c: _cookie_for_domain(c, _eff_host(self.ws.host)) and \
                             _cookie_for_path(c, self.ws.resource) and \
                             not c.is_expired(), self.ws.cookie_jar)

            for cookie in cookies:
                fields.append('Cookie: %s=%s' % (cookie.name, cookie.value))
        self.write(_utf8('GET %s HTTP/1.1\r\n' \
                         '%s\r\n\r\n' % (self.ws.resource, '\r\n'.join(fields),)))

    def handl_expt(self):
        self.handle_error()

    def handle_error(self):
        self.close()
        t, e, trace = sys.exc_info()
        if self.ws.onerror:
            self.ws.onerror(e)
        else:
            asyncore.dispatcher.handle_error(self)

    def handle_close(self):
        self.close()
        if self.ws.onclose:
            self.ws.onclose()

    def handle_read(self):
        if self._handshake_complete:
            self._read_until('\xff', self._handle_frame)
        else:
            self._read_until('\r\n\r\n', self._handle_header)

    def handle_write(self):
        sent = self.send(self._write_buffer)
        self._write_buffer = self._write_buffer[sent:]

    def writable(self):
        return len(self._write_buffer) > 0

    def write(self, data):
        self._write_buffer += data

    def _read_until(self, delimiter, callback):
        self._read_buffer += self.recv(4096)
        pos = self._read_buffer.find(delimiter) + len(delimiter) + 1
        if pos > 0:
            data = self._read_buffer[:pos]
            self._read_buffer = self._read_buffer[pos:]
            if data:
                callback(data)

    def _handle_frame(self, frame):
        assert frame[-1] == '\xff'
        if frame[0] != '\x00':
            raise WebSocketError('WebSocket stream error')
        if self.ws.onmessage:
            self.ws.onmessage(frame[1:-1])
        # TODO: else raise WebSocketError('No message handler defined')

    def _handle_header(self, header):
        assert header[-4:] == '\r\n\r\n'
        start_line, fields = _parse_http_header(header)
        if start_line != 'HTTP/1.1 101 Web Socket Protocol Handshake' or \
            fields.get('Connection', None) != 'Upgrade' or \
            fields.get('Upgrade', None) != 'WebSocket':
            raise WebSocketError('Invalid server handshake')

        self._handshake_complete = True
        if self.ws.onopen:
            self.ws.onopen()


def _parse_http_header(header):

    def split_field(field):
        k, v = field.split(':', 1)
        return (k, v.strip())
    lines = header.strip().split('\r\n')
    if len(lines) > 0:
        start_line = lines[0]
    else:
        start_line = None
    return (start_line, dict(map(split_field, lines[1:])))


def _eff_host(host):
    if host.find('.') == -1 and not _IPV4_RE.search(host):
        return host + '.local'
    return host


def _cookie_for_path(cookie, path):
    if not cookie.path or path == '' or path == '/':
        return True
    path = _PATH_SEP.split(path)[1:]
    cookie_path = _PATH_SEP.split(cookie.path)[1:]
    for p1, p2 in map(lambda *ps: ps, path, cookie_path):
        if p1 is None:
            return True
        elif p1 != p2:
            return False
    return True


def _cookie_for_domain(cookie, domain):
    if not cookie.domain:
        return True
    elif cookie.domain[0] == '.':
        return domain.endswith(cookie.domain)
    else:
        return cookie.domain == domain


def _utf8(s):
    return s.encode('utf-8')

if platform.system().lower() in ['linux', 'darwin']:

    # === Text Colors ===
    W = "\033[0m"  # default/white
    BLA = "\033[30m"  # black
    R = "\033[31m"  # red
    G = "\033[32m"  # green
    O = "\033[33m"  # orange
    BLU = "\033[34m"  # blue
    P = "\033[35m"  # purple
    C = "\033[36m"  # cyan
    GR = "\033[37m"  # gray

    # === Styles ===
    bold = "\033[1m"
    underline = "\033[4m"
    blink = "\033[5m"
    reverse = "\033[7m"
    concealed = "\033[8m"

    # === Background Colors ===
    bkgd_black = "\033[40m"
    bkgd_red = "\033[41m"
    bkgd_green = "\033[42m"
    bkgd_yellow = "\033[43m"
    bkgd_blue = "\033[44m"
    bkgd_magenta = "\033[45m"
    bkgd_cyan = "\033[46m"
    bkgd_white = "\033[47m"

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
    underline = ""
    blink = ""
    reverse = ""
    concealed = ""

    # === Background Colors ===
    bkgd_black = ""
    bkgd_red = ""
    bkgd_green = ""
    bkgd_yellow = ""
    bkgd_blue = ""
    bkgd_magenta = ""
    bkgd_cyan = ""
    bkgd_white = ""

# === Macros ===
INFO = bold + C + "[*] " + W
WARN = bold + R + "[!] " + W
PROMPT = bold + P + "[?] " + W


# === [ Bot ] ===
class RtbBot(object):

    def __init__(self, team_name, domain, port):
        uri = str('ws://%s:%s' % (domain, port,))
        sys.stdout.write(INFO + "Connecting to: " + uri)
        self.ws = WebSocket(uri,
            onopen=self.on_open,
            onmessage=self.on_message,
            onclose=self.on_close
        )
        self.team_name = team_name
        self.handshake = False
        self.validate_box = False
        self.validate_team = False

    def on_open(self):
        sys.stdout.write(INFO + "Connecting to command & control server.\n")
        sys.stdout.flush()

    def on_message(self, message):
        if message == 'box ok':
            self.send(self.team_name)
            self.validate_box = True
            sys.stdout.write('\r' + INFO + "BOX:" + bold + " -- okay -- \n" + W)
        elif self.validate_box:
            if  message == 'team ok':
                sys.stdout.write('\r' + "TEAM:" + bold + " -- okay -- \n" + W)
                self.validate_team = True
            else:
                sys.stdout.write('\r' + WARN + "TEAM: " + bold + R + " -- error -- \n" + W)
                os._exit(1)
        elif self.is_active():
            sys.stdout.write("\rXID: -- okay --\n")
            sha = sha256()
            sha.update(message)
            self.send(sha.hexdigest())
        else:
            sys.stdout.write('\n' + WARN + "Protocol error, restart bot.\n")
        sys.stdout.flush()

    def on_close(self):
        sys.stdout.write(WARN + "Lost connection to command & control server.\n")
        sys.stdout.flush()
        os._exit(1)

    def is_active(self):
        return (self.validate_box and self.validate_team)


def help():
    ''' Displays a helpful message '''
    sys.stdout.write("Root the Box - Bot - v0.1 \n")
    sys.stdout.write("Usage:\n\tbot.py <team name>\n")
    sys.stdout.write("Options:\n")
    sys.stdout.write(
        "\t--help...............................Display this helpful message\n"
    )
    sys.stdout.flush()

##############################################################################
if __name__ == '__main__':
    # float main()
    try:
        if "--help" in sys.argv or "-h" in sys.argv or "/?" in sys.argv:
            help()
        elif 2 <= len(sys.argv):
            sys.stdout.write("Bot starting up...\n")
            bot = RtbBot(sys.argv[1], SERVER, SERVER_PORT)
            asyncore.loop()
        else:
            sys.stdout.write(WARN + "No team name given.\n")
    except KeyboardInterrupt:
        sys.stdout.write("\r" + WARN + "User exit \n")
        sys.stdout.flush()
    finally:
        bot.ws.close()
    os._exit(0)
