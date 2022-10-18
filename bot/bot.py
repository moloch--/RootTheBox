#!/usr/bin/env python3
"""
@author: moloch
Copyright 2012 Root the Box
Created on Feb 24, 2012

---------
websocket - WebSocket client library for Python

Copyright (C) 2010 Hiroki Ohtani(liris)

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
---------

"""
# pylint: disable=unused-variable


import os
import sys
import json
import uuid
import array
import socket
import ssl
import struct
import base64
import hashlib
import logging
import argparse
import platform
import traceback
import codecs

from builtins import str

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from datetime import datetime
from hashlib import sha512, sha1
from builtins import range, object, chr


### Settings
__version__ = "0.1.1"
__domain__ = "game.rootthebox.com"
__desc__ = "Root the Box: Botnet"
__port__ = "80"
__path__ = "botnet/connect"

if platform.system().lower() in ["linux", "darwin"]:

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
INFO = bold + C + "[*]" + W
WARN = bold + R + "[!]" + W
PROMPT = bold + P + "[?]" + W
current_time = lambda: str(datetime.now()).split(" ")[1].split(".")[0]

"""
websocket python client.
=========================

This version support only hybi-13.
Please see http://tools.ietf.org/html/rfc6455 for protocol.
"""

# websocket supported version.
VERSION = 13

# closing frame status codes.
STATUS_NORMAL = 1000
STATUS_GOING_AWAY = 1001
STATUS_PROTOCOL_ERROR = 1002
STATUS_UNSUPPORTED_DATA_TYPE = 1003
STATUS_STATUS_NOT_AVAILABLE = 1005
STATUS_ABNORMAL_CLOSED = 1006
STATUS_INVALID_PAYLOAD = 1007
STATUS_POLICY_VIOLATION = 1008
STATUS_MESSAGE_TOO_BIG = 1009
STATUS_INVALID_EXTENSION = 1010
STATUS_UNEXPECTED_CONDITION = 1011
STATUS_TLS_HANDSHAKE_ERROR = 1015

logger = logging.getLogger()


class WebSocketException(Exception):
    """
    websocket exception class.
    """

    pass


class WebSocketConnectionClosedException(WebSocketException):
    """
    If remote host closed the connection or some network error happened,
    this exception will be raised.
    """

    pass


default_timeout = None
traceEnabled = False


def enableTrace(tracable):
    """
    turn on/off the tracability.

    tracable: boolean value. if set True, tracability is enabled.
    """
    global traceEnabled
    traceEnabled = tracable
    if tracable:
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)


def setdefaulttimeout(timeout):
    """
    Set the global timeout setting to connect.

    timeout: default socket timeout time. This value is second.
    """
    global default_timeout
    default_timeout = timeout


def getdefaulttimeout():
    """
    Return the global timeout setting(second) to connect.
    """
    return default_timeout


def _parse_url(url):
    """
    parse url and the result is tuple of
    (hostname, port, resource path and the flag of secure mode)

    url: url string.
    """
    if ":" not in url:
        raise ValueError("url is invalid")

    scheme, url = url.split(":", 1)

    parsed = urlparse(url, scheme="http")
    if parsed.hostname:
        hostname = parsed.hostname
    else:
        raise ValueError("hostname is invalid")
    port = 0
    if parsed.port:
        port = parsed.port

    is_secure = False
    if scheme == "ws":
        if not port:
            port = 80
    elif scheme == "wss":
        is_secure = True
        if not port:
            port = 443
    else:
        raise ValueError("scheme %s is invalid" % scheme)

    if parsed.path:
        resource = parsed.path
    else:
        resource = "/"

    if parsed.query:
        resource += "?" + parsed.query

    return (hostname, port, resource, is_secure)


def create_connection(url, timeout=None, **options):
    """
    connect to url and return websocket object.

    Connect to url and return the WebSocket object.
    Passing optional timeout parameter will set the timeout on the socket.
    If no timeout is supplied, the global default timeout setting returned by getdefauttimeout() is used.
    You can customize using 'options'.
    If you set "header" dict object, you can set your own custom header.

    >>> conn = create_connection("ws://echo.websocket.org/",
         ...     header=["User-Agent: MyProgram",
         ...             "x-custom: header"])


    timeout: socket timeout time. This value is integer.
             if you set None for this value, it means "use default_timeout value"

    options: current support option is only "header".
             if you set header as dict value, the custom HTTP headers are added.
    """
    sockopt = options.get("sockopt", ())
    websock = WebSocket(sockopt=sockopt)
    websock.settimeout(timeout != None and timeout or default_timeout)
    websock.connect(url, **options)
    return websock


_MAX_INTEGER = (1 << 32) - 1
_AVAILABLE_KEY_CHARS = list(range(0x21, 0x2F + 1)) + list(range(0x3A, 0x7E + 1))
_MAX_CHAR_BYTE = (1 << 8) - 1

# ref. Websocket gets an update, and it breaks stuff.
# http://axod.blogspot.com/2010/06/websocket-gets-update-and-it-breaks.html


def _create_sec_websocket_key():
    uid = uuid.uuid4()
    return decode(base64.encodestring(uid.bytes).strip())


_HEADERS_TO_CHECK = {"upgrade": "websocket", "connection": "upgrade"}


def encode(s, name="utf-8", *args, **kwargs):
    codec = codecs.lookup(name)
    rv, length = codec.encode(s, *args, **kwargs)
    if not isinstance(rv, (str, bytes, bytearray)):
        raise TypeError("Not a string or byte codec")
    return rv


def decode(s, name="utf-8", *args, **kwargs):
    codec = codecs.lookup(name)
    rv, length = codec.decode(s, *args, **kwargs)
    if not isinstance(rv, (str, bytes, bytearray)):
        raise TypeError("Not a string or byte codec")
    return rv


class _SSLSocketWrapper(object):
    def __init__(self, sock):
        self.ssl = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)

    def recv(self, bufsize):
        return self.ssl.read(bufsize)

    def send(self, payload):
        return self.ssl.write(payload)


_BOOL_VALUES = (0, 1)


def _is_bool(*values):
    for v in values:
        if v not in _BOOL_VALUES:
            return False

    return True


class ABNF(object):
    """
    ABNF frame class.
    see http://tools.ietf.org/html/rfc5234
    and http://tools.ietf.org/html/rfc6455#section-5.2
    """

    # operation code values.
    OPCODE_TEXT = 0x1
    OPCODE_BINARY = 0x2
    OPCODE_CLOSE = 0x8
    OPCODE_PING = 0x9
    OPCODE_PONG = 0xA

    # available operation code value tuple
    OPCODES = (OPCODE_TEXT, OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG)

    # opcode human readable string
    OPCODE_MAP = {
        OPCODE_TEXT: "text",
        OPCODE_BINARY: "binary",
        OPCODE_CLOSE: "close",
        OPCODE_PING: "ping",
        OPCODE_PONG: "pong",
    }

    # data length threshold.
    LENGTH_7 = 0x7D
    LENGTH_16 = 1 << 16
    LENGTH_63 = 1 << 63

    def __init__(
        self, fin=0, rsv1=0, rsv2=0, rsv3=0, opcode=OPCODE_TEXT, mask=1, data=""
    ):
        """
        Constructor for ABNF.
        please check RFC for arguments.
        """
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.opcode = opcode
        self.mask = mask
        self.data = data
        self.get_mask_key = os.urandom

    @staticmethod
    def create_frame(data, opcode):
        """
        create frame to send text, binary and other data.

        data: data to send. This is string value(byte array).
            if opcode is OPCODE_TEXT and this value is uniocde,
            data value is converted into unicode string, automatically.

        opcode: operation code. please see OPCODE_XXX.
        """
        if opcode == ABNF.OPCODE_TEXT and isinstance(data, str):
            data = data
        # mask must be set if send data from client
        return ABNF(1, 0, 0, 0, opcode, 1, data)

    def format(self):
        """
        format this object to string(byte array) to send data to server.
        """
        if not _is_bool(self.fin, self.rsv1, self.rsv2, self.rsv3):
            raise ValueError("not 0 or 1")
        if self.opcode not in ABNF.OPCODES:
            raise ValueError("Invalid OPCODE")
        length = len(self.data)
        if length >= ABNF.LENGTH_63:
            raise ValueError("data is too long")
        frame_header = struct.pack(
            "B",
            self.fin << 7
            | self.rsv1 << 6
            | self.rsv2 << 5
            | self.rsv3 << 4
            | self.opcode,
        )
        if length < ABNF.LENGTH_7:
            frame_header += struct.pack("B", self.mask << 7 | length)
        elif length < ABNF.LENGTH_16:
            frame_header += struct.pack("B", self.mask << 7 | 0x7E)
            frame_header += struct.pack("!H", length)
        else:
            frame_header += struct.pack("B", self.mask << 7 | 0x7F)
            frame_header += struct.pack("!Q", length)
        if not self.mask:
            return frame_header + encode(self.data)
        else:
            mask_key = self.get_mask_key(4)
            return frame_header + self._get_masked(mask_key)

    def _get_masked(self, mask_key):
        mask = ABNF.mask_data(mask_key, self.data)
        return mask_key + mask

    @staticmethod
    def mask_data(mask_key, data):
        """
        mask or unmask data. Just do xor for each byte

        mask_key: 4 byte string(byte).

        data: data to mask/unmask.
        """
        _m = array.array("B", mask_key)
        _d = array.array("B", encode(data))
        for i in range(len(_d)):
            _d[i] ^= _m[i % 4]
        return _d.tostring()


class WebSocket(object):
    """
    Low level WebSocket interface.
    This class is based on
      The WebSocket protocol draft-hixie-thewebsocketprotocol-76
      http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76

    We can connect to the websocket server and send/receive data.
    The following example is a echo client.

    >>> import websocket
    >>> ws = websocket.WebSocket()
    >>> ws.connect("ws://echo.websocket.org")
    >>> ws.send("Hello, Server")
    >>> ws.recv()
    'Hello, Server'
    >>> ws.close()

    get_mask_key: a callable to produce new mask keys, see the set_mask_key
      function's docstring for more details
    sockopt: values for socket.setsockopt.
        sockopt must be tuple and each element is argument of sock.setscokopt.
    """

    def __init__(self, get_mask_key=None, sockopt=()):
        """
        Initialize WebSocket object.
        """
        self.connected = False
        self.io_sock = self.sock = socket.socket()
        for opts in sockopt:
            self.sock.setsockopt(*opts)
        self.get_mask_key = get_mask_key

    def set_mask_key(self, func):
        """
        set function to create musk key. You can custumize mask key generator.
        Mainly, this is for testing purpose.

        func: callable object. the fuct must 1 argument as integer.
              The argument means length of mask key.
              This func must be return string(byte array),
              which length is argument specified.
        """
        self.get_mask_key = func

    def settimeout(self, timeout):
        """
        Set the timeout to the websocket.

        timeout: timeout time(second).
        """
        self.sock.settimeout(timeout)

    def gettimeout(self):
        """
        Get the websocket timeout(second).
        """
        return self.sock.gettimeout()

    def connect(self, url, **options):
        """
        Connect to url. url is websocket url scheme. ie. ws://host:port/resource
        You can customize using 'options'.
        If you set "header" dict object, you can set your own custom header.

        >>> ws = WebSocket()
        >>> ws.connect("ws://echo.websocket.org/",
                ...     header={"User-Agent: MyProgram",
                ...             "x-custom: header"})

        timeout: socket timeout time. This value is integer.
                 if you set None for this value,
                 it means "use default_timeout value"

        options: current support option is only "header".
                 if you set header as dict value,
                 the custom HTTP headers are added.

        """
        hostname, port, resource, is_secure = _parse_url(url)
        # TODO: we need to support proxy
        self.sock.connect((hostname, port))
        if is_secure:
            self.io_sock = _SSLSocketWrapper(self.sock)
        self._handshake(hostname, port, resource, **options)

    def _handshake(self, host, port, resource, **options):
        sock = self.io_sock
        headers = []
        headers.append("GET %s HTTP/1.1" % resource)
        headers.append("Upgrade: websocket")
        headers.append("Connection: Upgrade")
        if port == 80:
            hostport = host
        else:
            hostport = "%s:%d" % (host, port)
        headers.append("Host: %s" % hostport)

        if "origin" in options:
            headers.append("Origin: %s" % options["origin"])
        else:
            headers.append("Origin: http://%s" % hostport)

        key = _create_sec_websocket_key()
        headers.append("Sec-WebSocket-Key: %s" % key)
        headers.append("Sec-WebSocket-Version: %s" % VERSION)
        if "header" in options:
            headers.extend(options["header"])

        headers.append("")
        headers.append("")

        header_str = encode("\r\n".join(headers), "utf-8")
        sock.send(header_str)
        if traceEnabled:
            logger.debug("--- request header ---")
            logger.debug(decode(header_str))
            logger.debug("-----------------------")

        status, resp_headers = self._read_headers()
        if status != 101:
            self.close()
            raise WebSocketException("Handshake Status %d" % status)

        success = self._validate_header(resp_headers, key)
        if not success:
            self.close()
            raise WebSocketException("Invalid WebSocket Header")

        self.connected = True

    def _validate_header(self, headers, key):
        for k, v in list(_HEADERS_TO_CHECK.items()):
            r = headers.get(k, None)
            if not r:
                return False
            r = r.lower()
            if v != r:
                return False

        result = headers.get("sec-websocket-accept", None)
        if not result:
            return False
        result = result.lower()

        value = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        hashed = decode(
            base64.encodestring(hashlib.sha1(encode(value)).digest()).strip().lower()
        )
        return hashed == result

    def _read_headers(self):
        status = None
        headers = {}
        if traceEnabled:
            logger.debug("--- response header ---")

        while True:
            line = self._recv_line()
            if line == "\r\n":
                break
            line = line.strip()
            if traceEnabled:
                logger.debug(line)
            if not status:
                status_info = line.split(" ", 2)
                status = int(status_info[1])
            else:
                kv = line.split(":", 1)
                if len(kv) == 2:
                    key, value = kv
                    headers[key.lower()] = value.strip().lower()
                else:
                    raise WebSocketException("Invalid header")

        if traceEnabled:
            logger.debug("-----------------------")

        return status, headers

    def send(self, payload, opcode=ABNF.OPCODE_TEXT):
        """
        Send the data as string.

        payload: Payload must be utf-8 string or unicoce,
                  if the opcode is OPCODE_TEXT.
                  Otherwise, it must be string(byte array)

        opcode: operation code to send. Please see OPCODE_XXX.
        """
        if traceEnabled:
            logger.debug("send: " + repr(payload))
        frame = ABNF.create_frame(payload, opcode)
        if self.get_mask_key:
            frame.get_mask_key = self.get_mask_key
        data = frame.format()
        while data:
            l = self.io_sock.send(data)
            data = data[l:]

    def ping(self, payload=""):
        """
        send ping data.

        payload: data payload to send server.
        """
        self.send(payload, ABNF.OPCODE_PING)

    def pong(self, payload):
        """
        send pong data.

        payload: data payload to send server.
        """
        self.send(payload, ABNF.OPCODE_PONG)

    def recv(self):
        """
        Receive string data(byte array) from the server.

        return value: string(byte array) value.
        """
        opcode, data = self.recv_data()
        return data

    def recv_data(self):
        """
        Receive data with operation code.

        return  value: tuple of operation code and string(byte array) value.
        """
        while True:
            frame = self.recv_frame()
            if not frame:
                # handle error:
                # 'NoneType' object has no attribute 'opcode'
                raise WebSocketException("Not a valid frame %s" % frame)
            elif frame.opcode in (ABNF.OPCODE_TEXT, ABNF.OPCODE_BINARY):
                return (frame.opcode, frame.data)
            elif frame.opcode == ABNF.OPCODE_CLOSE:
                self.send_close()
                return (frame.opcode, None)
            elif frame.opcode == ABNF.OPCODE_PING:
                self.pong(frame.data)

    def recv_frame(self):
        """
        Receive data as frame from server.

        return value: ABNF frame object.
        """
        header_bytes = self._recv_strict(2)
        if not header_bytes:
            return None
        if isinstance(header_bytes[0], int):
            b1 = header_bytes[0]
        else:
            b1 = ord(header_bytes[0])
        fin = b1 >> 7 & 1
        rsv1 = b1 >> 6 & 1
        rsv2 = b1 >> 5 & 1
        rsv3 = b1 >> 4 & 1
        opcode = b1 & 0xF
        if isinstance(header_bytes[1], int):
            b2 = header_bytes[1]
        else:
            b2 = ord(header_bytes[1])
        mask = b2 >> 7 & 1
        length = b2 & 0x7F

        length_data = ""
        if length == 0x7E:
            length_data = self._recv_strict(2)
            length = struct.unpack("!H", length_data)[0]
        elif length == 0x7F:
            length_data = self._recv_strict(8)
            length = struct.unpack("!Q", length_data)[0]

        mask_key = ""
        if mask:
            mask_key = self._recv_strict(4)
        data = self._recv_strict(length)

        if traceEnabled:
            received = header_bytes + encode(length_data) + encode(mask_key) + data
            logger.debug("recv: " + repr(received))

        if mask:
            data = ABNF.mask_data(mask_key, data)

        frame = ABNF(fin, rsv1, rsv2, rsv3, opcode, mask, data)
        return frame

    def send_close(self, status=STATUS_NORMAL, reason=""):
        """
        send close data to the server.

        status: status code to send. see STATUS_XXX.

        reason: the reason to close. This must be string.
        """
        if status < 0 or status >= ABNF.LENGTH_16:
            raise ValueError("code is invalid range")
        self.send("%s%s" % (struct.pack("!H", status), reason), ABNF.OPCODE_CLOSE)

    def close(self, status=STATUS_NORMAL, reason=""):
        """
        Close Websocket object

        status: status code to send. see STATUS_XXX.

        reason: the reason to close. This must be string.
        """
        if self.connected:
            if status < 0 or status >= ABNF.LENGTH_16:
                raise ValueError("code is invalid range")

            try:
                self.send(struct.pack("!H", status) + reason, ABNF.OPCODE_CLOSE)
                timeout = self.sock.gettimeout()
                self.sock.settimeout(3)
                try:
                    frame = self.recv_frame()
                    if logger.isEnabledFor(logging.ERROR):
                        recv_status = struct.unpack("!H", frame.data)[0]
                        if recv_status != STATUS_NORMAL:
                            logger.error("close status: " + repr(recv_status))
                except:
                    pass
                self.sock.settimeout(timeout)
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
        self._closeInternal()

    def _closeInternal(self):
        self.connected = False
        self.sock.close()
        self.io_sock = self.sock

    def _recv(self, bufsize):
        bytes_val = self.io_sock.recv(bufsize)
        if not bytes_val:
            raise WebSocketConnectionClosedException()
        return bytes_val

    def _recv_strict(self, bufsize):
        remaining = bufsize
        bytes_val = b""
        while remaining:
            bytes_val += self._recv(remaining)
            remaining = bufsize - len(bytes_val)
        return bytes_val

    def _recv_line(self):
        line = []
        while True:
            c = decode(self._recv(1))
            line.append(c)
            if c == "\n":
                break
        return "".join(line)


class WebSocketApp(object):
    """
    Higher level of APIs are provided.
    The interface is like JavaScript WebSocket object.
    """

    def __init__(
        self,
        url,
        header=[],
        on_open=None,
        on_message=None,
        on_error=None,
        on_close=None,
        keep_running=True,
        get_mask_key=None,
        sockopt=(),
    ):
        """
         url: websocket url.
         header: custom header for websocket handshake.
         on_open: callable object which is called at opening websocket.
           this function has one argument. The argument is this class object.
         on_message: callbale object which is called when received data.
          on_message has 2 arguments.
          The 1st argument is this class object.
          The passing 2nd argument is utf-8 string which we get from the server.
        on_error: callable object which is called when we get error.
          on_error has 2 arguments.
          The 1st argument is this class object.
          The passing 2nd argument is exception object.
        on_close: callable object which is called when closed the connection.
          this function has one argument. The argument is this class object.
        keep_running: a boolean flag indicating whether the app's main loop should
          keep running, defaults to True
        get_mask_key: a callable to produce new mask keys, see the WebSocket.set_mask_key's
          docstring for more information
        """
        self.url = url
        self.header = header
        self.on_open = on_open
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.keep_running = keep_running
        self.get_mask_key = get_mask_key
        self.sock = None

    def send(self, data, opcode=ABNF.OPCODE_TEXT):
        """
        send message.
        data: message to send. If you set opcode to OPCODE_TEXT, data must be utf-8 string or unicode.
        opcode: operation code of data. default is OPCODE_TEXT.
        """
        if self.sock.send(data, opcode) == 0:
            raise WebSocketConnectionClosedException()

    def close(self):
        """
        close websocket connection.
        """
        self.keep_running = False
        self.sock.close()

    def run_forever(self, sockopt=()):
        """
        run event loop for WebSocket framework.
        This loop is infinite loop and is alive during websocket is available.
        sockopt: values for socket.setsockopt.
            sockopt must be tuple and each element is argument of sock.setscokopt.
        """
        if self.sock:
            raise WebSocketException("socket is already opened")
        try:
            self.sock = WebSocket(self.get_mask_key, sockopt=sockopt)
            self.sock.connect(self.url, header=self.header)
            self._run_with_no_err(self.on_open)
            while self.keep_running:
                data = self.sock.recv()
                if data is None:
                    break
                self._run_with_no_err(self.on_message, data)
        except Exception as e:
            self._run_with_no_err(self.on_error, e)
        finally:
            self.sock.close()
            self._run_with_no_err(self.on_close)
            self.sock = None

    def _run_with_no_err(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.error(e)


#############################################################################################
### [ Messages ] ############################################################################
#############################################################################################


def display_error(ws, response, verbose=False):
    msg = response["message"] if "message" in response else response["error"]
    sys.stderr.write("\n%s %s Error  : %s" % (WARN, current_time(), msg))
    if (ws is not None and ws.verbose) or verbose:
        sys.stderr.write("\n")
        traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()


def display_status(ws, response, verbose=False):
    sys.stdout.write(chr(27) + "[2K" + "\r")
    sys.stdout.write("%s %s Status : %s " % (INFO, current_time(), response["message"]))
    if (ws is not None and ws.verbose) or verbose:
        sys.stdout.write("\n")
    sys.stdout.flush()


def get_response_xid(garbage, xid):
    round1 = encode(sha512(encode(xid + garbage)).hexdigest())
    print("Garbage: " + garbage)
    print("XID :" + xid)
    print("[*] Return: " + str(sha512(round1).hexdigest()))
    return sha512(round1).hexdigest()


def send_interrogation_response(ws, response):
    display_status(ws, {"message": "Authorizing, please wait ..."})
    solved_xid = {
        "opcode": "interrogation_response",
        "response_xid": get_response_xid(ws.garbage, response["xid"]),
        "box_name": decode(ws.box_name),
        "handle": ws.user,
    }
    ws.send(json.dumps(solved_xid))


def recv_ping(ws, response, verbose=False):
    """Print that we just got a ping from c&c"""
    sys.stdout.write(chr(27) + "[2K" + "\r")
    sys.stdout.write(
        INFO + " %s  Ping  : Received a ping from command & control" % current_time()
    )
    if (ws is not None and ws.verbose) or verbose:
        sys.stdout.write("\n")
    sys.stdout.flush()


opcodes = {
    "error": display_error,
    "status": display_status,
    "interrogate": send_interrogation_response,
    "ping": recv_ping,
}


def on_open(ws):
    display_status(ws, {"message": "Successfully connected to command & control ..."})


def on_message(ws, message):
    """Parse message and call a function"""
    try:
        response = json.loads(message)
        if "opcode" not in response:
            raise ValueError("Missing opcode")
        elif response["opcode"] not in opcodes:
            raise ValueError("Invalid opcode")
        else:
            opcodes[response["opcode"]](ws, response)
    except ValueError as error:
        display_error(ws, {"error": str(error)})


def on_error(ws, error):
    display_error(ws, {"error": str(error)})


def on_close(ws):
    display_error(ws, {"error": "Disconnected from command & control\n"})


def get_default_garbage():
    return (
        "/root/garbage"
        if platform.system().lower() in ["linux", "darwin"]
        else "C:\\garbage"
    )


def main(domain, port, user, garbage_path, secure, verbose):
    """Main()"""
    garbage_cfg = ConfigParser.SafeConfigParser()
    if garbage_path is None:
        garbage_path = get_default_garbage()
    if not os.path.exists(garbage_path):
        print(WARN + " Garbage file not found %s" % garbage_path)
        os._exit(1)
    fp = open(garbage_path, "r")
    try:
        garbage_cfg.readfp(fp)
    except:
        print(WARN + " Garbage file is not properly formatted")
        os._exit(2)
    try:
        enableTrace(verbose)
        connection_url = "ws://%s:%s/%s" % (domain, port, __path__)
        display_status(
            None, {"message": "Connecting to: %s" % connection_url}, verbose=verbose
        )
        ws = WebSocketApp(
            connection_url, on_message=on_message, on_error=on_error, on_close=on_close
        )
        ws.verbose = verbose
        ws.garbage = garbage_cfg.get("Bot", "garbage")
        ws.box_name = decode(garbage_cfg.get("Bot", "name"), "hex")
        ws.user = user
        ws.on_open = on_open
        ws.run_forever()
    except KeyboardInterrupt:
        os._exit(0)
    except Exception as error:
        display_error(None, {"error": str(error)})
        os._exit(1)


##############################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__desc__)
    parser.add_argument(
        "--version", action="version", version="%(prog)s v" + __version__
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="display verbose output (default: false)",
        action="store_true",
        dest="verbose",
    )
    parser.add_argument(
        "--secure",
        "-s",
        help="connect using a secure socket (default: false)",
        action="store_true",
        dest="secure",
    )
    parser.add_argument(
        "--garbage",
        "-g",
        help="path to garbage file (default: /root/garbage or C:\\garbage)",
        dest="garbage",
    )
    parser.add_argument(
        "--domain",
        "-d",
        help="scoring engine ip address, or domain (default: %s)" % __domain__,
        default=__domain__,
        dest="domain",
    )
    parser.add_argument(
        "--port",
        "-p",
        help="netork port to connect to (default: %s)" % __port__,
        default=__port__,
        dest="port",
    )
    parser.add_argument(
        "--user",
        "-u",
        help="your handle (scoring engine account name)",
        required=True,
        dest="handle",
    )
    args = parser.parse_args()
    main(args.domain, args.port, args.handle, args.garbage, args.secure, args.verbose)
