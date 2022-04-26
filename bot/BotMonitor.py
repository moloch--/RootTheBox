#!/usr/bin/env python3
"""
Created on Apr 23, 2012
@author: moloch

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

Linux/OSX only (well anything with curses really)
Small program used by teams to monitor their flags
For the sake of portability everything is in one file

"""

# pylint: disable=unused-variable
###################
# > Imports
###################
import os
import sys
import time
import json
import uuid
import array
import struct
import base64
import socket
import random
import hashlib
import logging
import argparse
import platform
import threading
from builtins import range, object, chr, str
from past.utils import old_div

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from datetime import datetime
from libs.StringCoding import encode

try:
    import curses
    import curses.panel
except ImportError:
    sys.stdout.write("Error: Failed to import curses, platform not supported\n")
    os._exit(2)

###################
# > Constants
###################
BUFFER_SIZE = 64
MIN_Y = 24
MIN_X = 80

###################
# > Defaults
###################
__version__ = "0.1.1"
__port__ = "8888"
__domain__ = "localhost"
__path__ = "/botnet/climonitor"
__log__ = "bot_monitor.log"

###################
# > Logging
###################
LOG_LEVELS = {
    "notset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "critical": logging.CRITICAL,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
}
logger = logging.getLogger()

###################
# > Websockets
###################
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


def enableTrace(traceable):
    """
    turn on/off the traceability.

    traceable: boolean value. if set True, traceability is enabled.
    """
    global traceEnabled
    traceEnabled = traceable
    if traceable:
        logger.setLevel(logging.DEBUG)


def setdefaulttimeout(timeout):
    """
    Set the global timeout setting to connect.

    timeout: default socket timeout time. This value is second.
    """
    global default_timeout
    default_timeout = int(timeout)
    if default_timeout < 30:
        default_timeout = 30
    logging.info("Socket timeout set to: %d" % timeout)


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
    If no timeout is supplied, the global default timeout setting returned by getdefaulttimeout() is used.
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
    actual_timeout = timeout is not None and timeout or default_timeout
    logging.info("[Socket] Timeout: %d" % actual_timeout)
    websock.settimeout(actual_timeout)
    websock.connect(url, **options)
    return websock


_MAX_INTEGER = (1 << 32) - 1
_AVAILABLE_KEY_CHARS = list(range(0x21, 0x2F + 1)) + list(range(0x3A, 0x7E + 1))
_MAX_CHAR_BYTE = (1 << 8) - 1

# ref. Websocket gets an update, and it breaks stuff.
# http://axod.blogspot.com/2010/06/websocket-gets-update-and-it-breaks.html


def _create_sec_websocket_key():
    uid = uuid.uuid4()
    return base64.encodestring(uid.bytes).strip()


_HEADERS_TO_CHECK = {"upgrade": "websocket", "connection": "upgrade"}


class _SSLSocketWrapper(object):
    def __init__(self, sock):
        self.ssl = socket.ssl(sock)

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
            if opcode is OPCODE_TEXT and this value is unicode,
            data value is converted into unicode string, automatically.

        opcode: operation code. please see OPCODE_XXX.
        """
        if sys.version_info.major == 2:
            instance = isinstance(data, unicode)
        else:
            instance = isinstance(data, str)
        if opcode == ABNF.OPCODE_TEXT and instance:
            data = encode(data, "utf-8")
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

        frame_header = chr(
            self.fin << 7
            | self.rsv1 << 6
            | self.rsv2 << 5
            | self.rsv3 << 4
            | self.opcode
        )
        if length < ABNF.LENGTH_7:
            frame_header += chr(self.mask << 7 | length)
        elif length < ABNF.LENGTH_16:
            frame_header += chr(self.mask << 7 | 0x7E)
            frame_header += struct.pack("!H", length)
        else:
            frame_header += chr(self.mask << 7 | 0x7F)
            frame_header += struct.pack("!Q", length)

        if not self.mask:
            return frame_header + self.data
        else:
            mask_key = self.get_mask_key(4)
            return frame_header + self._get_masked(mask_key)

    def _get_masked(self, mask_key):
        s = ABNF.mask(mask_key, self.data)
        return mask_key + "".join(s)

    @staticmethod
    def mask(mask_key, data):
        """
        mask or unmask data. Just do xor for each byte

        mask_key: 4 byte string(byte).

        data: data to mask/unmask.
        """
        _m = array.array("B", mask_key)
        _d = array.array("B", data)
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
        sockopt must be tuple and each element is argument of sock.setsockopt.
    """

    def __init__(self, get_mask_key=None, sockopt=()):
        """
        Initialize WebSocket object.
        """
        self.connected = False
        self.monitor = None
        self.io_sock = self.sock = socket.socket()
        for opts in sockopt:
            self.sock.setsockopt(*opts)
        self.get_mask_key = get_mask_key

    def set_mask_key(self, func):
        """
        set function to create musk key. You can customize mask key generator.
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

        header_str = "\r\n".join(headers)
        sock.send(header_str)
        if traceEnabled:
            logger.debug("--- request header ---")
            logger.debug(header_str)
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
        hashed = base64.encodestring(hashlib.sha1(value).digest()).strip().lower()
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

        payload: Payload must be utf-8 string or unicode,
                  if the opcode is OPCODE_TEXT.
                  Otherwise, it must be string(byte array)

        opcode: operation code to send. Please see OPCODE_XXX.
        """
        frame = ABNF.create_frame(payload, opcode)
        if self.get_mask_key:
            frame.get_mask_key = self.get_mask_key
        data = frame.format()
        while data:
            l = self.io_sock.send(data)
            data = data[l:]
        if traceEnabled:
            logger.debug("send: " + repr(data))

    def ping(self, payload=""):
        """
        send ping data.

        payload: data payload to send server.
        """
        logging.debug("Got <- PING")
        self.send(payload, ABNF.OPCODE_PING)

    def pong(self, payload):
        """
        send pong data.

        payload: data payload to send server.
        """
        logging.debug("Sending -> PONG")
        self.monitor.pong = True
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
        receive data as frame from server.

        return value: ABNF frame object.
        """
        header_bytes = self._recv_strict(2)
        if not header_bytes:
            return None
        b1 = ord(header_bytes[0])
        fin = b1 >> 7 & 1
        rsv1 = b1 >> 6 & 1
        rsv2 = b1 >> 5 & 1
        rsv3 = b1 >> 4 & 1
        opcode = b1 & 0xF
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
            received = header_bytes + length_data + mask_key + data
            logger.debug("recv: " + repr(received))

        if mask:
            data = ABNF.mask(mask_key, data)

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
        self.send(struct.pack("!H", status) + reason, ABNF.OPCODE_CLOSE)

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
        bytes = self.io_sock.recv(bufsize)
        if not bytes:
            raise WebSocketConnectionClosedException()
        return bytes

    def _recv_strict(self, bufsize):
        remaining = bufsize
        bytes = ""
        while remaining:
            bytes += self._recv(remaining)
            remaining = bufsize - len(bytes)

        return bytes

    def _recv_line(self):
        line = []
        while True:
            c = self._recv(1)
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
        header=None,
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
        self.header = header or []
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
            sockopt must be tuple and each element is argument of sock.setsockopt.
        """
        if self.sock:
            raise WebSocketException("socket is already opened")
        try:
            self.sock = WebSocket(self.get_mask_key, sockopt=sockopt)
            self.sock.settimeout(getdefaulttimeout())
            self.sock.connect(self.url, header=self.header)
            self.sock.monitor = self.monitor
            self._run_with_no_err(self.on_open)
            while self.keep_running:
                data = self.sock.recv()
                if data is None:
                    break
                self._run_with_no_err(self.on_message, data)
        except KeyboardInterrupt:
            pass  # Just close and exit
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
            except Exception as err:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.error(err)


###################
# > Time to Str
###################
def current_time():
    """ Return current time as HH:MM:SS """
    return time.strftime("%H:%M:%S")


###################
# > Opcodes
###################
def stop_animate_thread(ws):
    """ Block until animation thread exits """
    logging.info("Waiting for animation thread to exit ...")
    ws.monitor.stop_thread = True
    if ws.monitor.animate_thread is not None:
        ws.monitor.animate_thread.join()
    logging.info("All threads have joined")
    ws.monitor.animate_thread = None
    ws.monitor.stop_thread = False


def update(ws, message):
    """ Recv and draw latest update """
    logging.debug("Got update: %s" % message)
    bots = []
    for bot in message["bots"]:
        bots.append((bot["box_name"], bot["remote_ip"], bot["total_reward"]))
    ws.monitor.update_grid(bots)


def auth_failure(ws, message):
    """ Failed to properly authenticate with scoring engine """
    stop_animate_thread(ws)
    logging.info("Authentication failure")
    ws.monitor.auth_failure("ACCESS DENIED")


def auth_success(ws, message):
    """ Successfully authenticated with scoring engine"""
    stop_animate_thread(ws)
    logging.info("Successfully authenticated")
    thread = threading.Thread(target=ws.monitor.progress)
    thread.start()
    ws.monitor.animate_thread = thread
    ws.monitor.__interface__()


def ping(ws, message):
    ws.monitor.pong = True


OPCODES = {}
OPCODES["update"] = update
OPCODES["auth_success"] = auth_success
OPCODES["auth_failure"] = auth_failure
OPCODES["ping"] = ping


###################
# > WS Callbacks
###################
def on_open(ws):
    """ Send auth when socket is open """
    logging.info("Sending credentials to engine")
    auth_msg = json.dumps(
        {"opcode": "auth", "handle": ws.agent_name, "password": ws.password}
    )
    ws.send(auth_msg)
    ws.monitor.stop_thread = False


def on_message(ws, message):
    """ Parse message and call a function """
    logging.debug("Recv'd message: %s" % str(message))
    try:
        response = json.loads(message)
        if "opcode" not in response:
            raise ValueError("Missing opcode")
        elif response["opcode"] not in OPCODES:
            raise ValueError("Invalid opcode")
        else:
            OPCODES[response["opcode"]](ws, response)
    except ValueError:
        ws.close()


def on_error(ws, error):
    """ Error recv'd on WebSocket """
    logging.exception("[WebSocket] on_error - %s" % type(error))
    stop_animate_thread(ws)
    if isinstance(error, socket.error):
        ws.monitor.connection_problems()
    elif isinstance(error, WebSocketException):
        ws.monitor.connection_problems()
    ws.monitor.stop()


def on_close(ws):
    """ Websocket closed """
    logging.debug("[WebSocket] Closing connection.")
    stop_animate_thread(ws)
    ws.monitor.stop("Connection lost")


###################
# > Bot Monitor
###################
class BotMonitor(object):
    """ Manages all flags and state changes """

    def __init__(self, connection_url):
        self.url = connection_url
        self.agent_name = None
        self.password = None
        self.total_income = 0
        self.animate_thread = None
        self.pong = False

    def start(self):
        """ Initializes the screen """
        self.screen = curses.initscr()
        self.__clear__()
        curses.start_color()
        curses.use_default_colors()
        self.__colors__()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.max_y, self.max_x = self.screen.getmaxyx()
        self.screen.border(0)
        self.screen.refresh()
        self.__load__()
        self.__connect__()

    def stop(self, message=None):
        """ Gracefully exits the program """
        logging.debug("Stopping curses ui: %s" % message)
        self.__clear__()
        curses.endwin()
        os._exit(0)

    def connection_problems(self):
        """ Display connection issue, and exit """
        logging.fatal("Connection failure!")
        self.auth_failure("CONNECTION FAILURE")

    def __connect__(self):
        """ Connect and authenticate with scoring engine """
        ws = WebSocketApp(
            self.url, on_message=on_message, on_error=on_error, on_close=on_close
        )
        ws.monitor = self
        ws.agent_name = self.agent_name
        ws.password = self.password
        ws.on_open = on_open
        self.animate_thread = threading.Thread(target=self.__connecting__)
        self.stop_thread = False
        self.animate_thread.start()
        ws.run_forever()

    def __connecting__(self):
        """ Display connecting animation """
        self.__clear__()
        self.screen.refresh()
        prompt = " Connecting, please wait ..."
        connecting = curses.newwin(
            3,
            len(prompt) + 2,
            (old_div(self.max_y, 2)) - 1,
            (old_div((self.max_x - len(prompt)), 2)),
        )
        connecting.clear()
        connecting.addstr(1, 1, prompt, curses.A_BOLD | curses.color_pair(self.CYAN))
        connecting.refresh()
        time.sleep(0.25)
        while not self.stop_thread:
            connecting.addstr(1, 1, " " * len(prompt))
            connecting.refresh()
            time.sleep(0.15)
            connecting.addstr(
                1, 1, prompt, curses.A_BOLD | curses.color_pair(self.CYAN)
            )
            connecting.refresh()
            time.sleep(0.25)
        connecting.endwin()

    def __load__(self):
        """ Loads all required data """
        self.load_message = " Loading, please wait ... "
        self.loading_bar = curses.newwin(
            3,
            len(self.load_message) + 2,
            (old_div(self.max_y, 2)) - 1,
            (old_div((self.max_x - len(self.load_message)), 2)),
        )
        self.loading_bar.border(0)
        self.loading_bar.addstr(1, 1, self.load_message, curses.A_BOLD)
        self.loading_bar.refresh()
        time.sleep(0.5)
        self.__credentials__()
        self.loading_bar.clear()

    def __interface__(self):
        """ Main interface loop """
        self.__redraw__()
        self.screen.nodelay(1)
        self.__title__()
        self.__grid__()
        self.__positions__()
        self.screen.refresh()

    def __title__(self):
        """ Create title and footer """
        title = " Root the Box: Botnet Monitor "
        start_x = old_div((self.max_x - len(title)), 2)
        self.screen.addstr(
            0, start_x, title, curses.A_BOLD | curses.color_pair(self.BLUE)
        )
        self.screen.addstr(0, start_x - 1, "|", curses.A_BOLD)
        self.screen.addstr(0, start_x + len(title), "|", curses.A_BOLD)
        # Bottom bar
        display_time = "[ %s ]" % current_time()
        self.screen.addstr(
            self.max_y - 1, (self.max_x - len(display_time)) - 3, display_time
        )
        self.screen.addstr(self.max_y - 1, 3, "[---]")

    def __grid__(self):
        """ Draws the grid layout """
        pos_x, pos_y = 3, 3
        self.screen.hline(2, 1, curses.ACS_HLINE, self.max_x - 2)
        self.screen.hline(4, 1, curses.ACS_HLINE, self.max_x - 2)
        # IP Address
        self.ip_title = "    IP  Address    "
        self.screen.addstr(pos_y, 2, self.ip_title)
        self.screen.vline(
            pos_y, pos_x + len(self.ip_title), curses.ACS_VLINE, self.max_y - 4
        )
        # Box Name
        pos_x += len(self.ip_title)
        self.name_title = "          Box  Name          "
        self.screen.addstr(pos_y, pos_x + 1, self.name_title)
        self.screen.vline(
            pos_y, pos_x + len(self.name_title) + 1, curses.ACS_VLINE, self.max_y - 4
        )
        # Bot Income
        pos_x += len(self.name_title)
        self.income_title = "    Bot  Income    "
        self.screen.addstr(pos_y, pos_x + 2, self.income_title)

    def __positions__(self):
        """ Calculates starting x position for each column """
        self.start_ip_pos = 2
        self.start_name_pos = self.start_ip_pos + len(self.ip_title) + 3
        self.start_income_pos = self.start_name_pos + len(self.name_title) + 1

    def update_grid(self, boxes):
        """ Redraw the grid with updated box information """
        self.__interface__()
        update_income = sum([box[2] for box in boxes])
        self.total_income += update_income
        self.__summary__(len(boxes), current_time())
        start_row = 5
        for index, box in enumerate(boxes):
            self.screen.addstr(
                start_row + index, self.start_ip_pos, "%d) %s" % (index + 1, box[0])
            )
            self.screen.addstr(start_row + index, self.start_name_pos, box[1])
            if 0 < float(update_income):
                percent = (old_div(float(box[2]), float(update_income))) * 100.0
                income_string = "$%d  (%.02d%s)" % (box[2], percent, "%")
            else:
                income_string = "$%d" % (box[2],)
            self.screen.addstr(start_row + index, self.start_income_pos, income_string)
        self.screen.refresh()

    def __summary__(self, bot_count, update_time):
        """ Adds total bots and update time """
        start_pos = 3
        pos_y = 1
        self.screen.addstr(
            pos_y, start_pos, "- Last Update: %s -" % update_time, curses.A_BOLD
        )
        bot_string = "$%d (%d bots)" % (self.total_income, bot_count)
        bot_pos = self.max_x - (len(bot_string) + 3)
        self.screen.addstr(pos_y, bot_pos, bot_string, curses.A_BOLD)

    def __colors__(self):
        """ Init colors pairs """
        self.NO_COLOR = -1
        self.RED = 1
        curses.init_pair(self.RED, curses.COLOR_RED, self.NO_COLOR)
        self.CYAN = 2
        curses.init_pair(self.CYAN, curses.COLOR_CYAN, self.NO_COLOR)
        self.WHITE_RED = 3
        curses.init_pair(self.WHITE_RED, curses.COLOR_WHITE, curses.COLOR_RED)
        self.BLUE = 4
        curses.init_pair(self.BLUE, curses.COLOR_BLUE, self.NO_COLOR)

    def __redraw__(self):
        """ Redraw the entire window """
        self.screen.clear()
        self.screen.border(0)
        self.screen.refresh()

    def __clear__(self):
        """ Clears the screen """
        self.screen.clear()
        self.screen.refresh()

    def __credentials__(self):
        """ Get display name from user """
        self.stop_thread = False
        thread = threading.Thread(target=self.__matrix__)
        self.loading_bar.clear()
        # Get agent name
        prompt = "Account: "
        self.agent_prompt = curses.newwin(
            3,
            len(self.load_message) + 2,
            (old_div(self.max_y, 2)) - 1,
            (old_div((self.max_x - len(self.load_message)), 2)),
        )
        self.agent_prompt.clear()
        self.agent_prompt.border(0)
        self.agent_prompt.addstr(1, 1, prompt, curses.A_BOLD)
        curses.echo()
        thread.start()
        self.agent_name = self.agent_prompt.getstr(
            1, len(prompt) + 1, len(self.load_message) - len(prompt) - 1
        )
        # Get password
        curses.noecho()
        prompt = "Password: "
        self.agent_prompt = curses.newwin(
            3,  # Height
            len(self.load_message) + 24,  # Width
            (old_div(self.max_y, 2)) - 1,  # Start Y
            (old_div((self.max_x - len(self.load_message)), 2)) - 12,  # Start X
        )
        self.agent_prompt.border(0)
        self.agent_prompt.addstr(1, 1, prompt, curses.A_BOLD)
        self.password = self.agent_prompt.getstr(1, len(prompt) + 1, 64)
        self.stop_thread = True
        thread.join()  # Wait for "Matrix" threads to stop

    def __matrix__(self):
        """ Displays really cool, pointless matrix like animation in the background """
        # (2) Sat com animation
        sat_com = " > Initializing sat com unit, please wait ... "
        progress = ["|", "/", "-", "\\"]
        for index in range(0, random.randint(50, 150)):
            self.screen.addstr(2, 2, sat_com + progress[index % 4])
            self.screen.refresh()
            time.sleep(0.1)
            if self.stop_thread:
                return
        self.screen.addstr(2, 2, sat_com + "success")
        self.screen.refresh()
        # (3) Uplink animation
        download = " > Establishing satellite uplink: "
        for index in range(5, 25):
            signal = random.randint(0, 30)
            self.screen.addstr(3, 2, download + str(signal) + " dBi    ")
            self.screen.refresh()
            time.sleep(0.2)
            if self.stop_thread:
                return
        self.screen.addstr(3, 2, download + "locked on")
        self.screen.refresh()
        # (4) Downloading animation
        download = " > Downloading noki telcodes: "
        for index in range(0, 100):
            self.screen.addstr(4, 2, download + str(index) + "%")
            self.screen.refresh()
            time.sleep(0.1)
            if self.stop_thread:
                return
        self.screen.addstr(4, 2, download + "complete")
        self.screen.refresh()
        # (5) Initializing memory address
        memory = " > Initializing memory: "
        for index in range(0, 2 ** 32, 2 ** 20):
            time.sleep(0.02)
            self.screen.addstr(5, 2, memory + str("0x%08X" % index))
            self.screen.refresh()
            if self.stop_thread:
                return
        self.screen.addstr(5, 2, memory + str("0x%08X -> 0xFFFFFFFF" % (0,)))
        self.screen.refresh()
        # (6) Matrix animation
        matrix = " > The matrix has you ... follow the white rabbit "
        for index in range(0, len(matrix)):
            time.sleep(0.2)
            self.screen.addstr(6, 2, matrix[:index])
            self.screen.refresh()
            if self.stop_thread:
                return

    def progress(self):
        """ Progress animation, executed as separate thread """
        index = 0
        progress_bar = ["=--", "-=-", "--=", "-=-"]
        pong_string = "PNG"
        while not self.stop_thread:
            if self.pong:
                self.screen.addstr(self.max_y - 1, 3, "[")
                self.screen.addstr(
                    self.max_y - 1, 4, pong_string, curses.color_pair(self.WHITE_RED)
                )
                self.screen.addstr(self.max_y - 1, 7, "]")
                self.pong = False
            else:
                index += 1
                progress_string = "[%s]" % (progress_bar[index % len(progress_bar)])
                self.screen.addstr(self.max_y - 1, 3, progress_string)
            display_time = "[ %s ]" % current_time()
            self.screen.addstr(
                self.max_y - 1, (self.max_x - len(display_time)) - 3, display_time
            )
            self.screen.refresh()
            time.sleep(0.2)

    def auth_failure(self, msg):
        """ Display authentication failure message """
        logging.info("Displaying auth failure message")
        self.__clear__()
        self.screen.refresh()
        prompt = " *** %s *** " % msg
        access_denied = curses.newwin(
            3,
            len(prompt) + 2,
            (old_div(self.max_y, 2)) - 1,
            (old_div((self.max_x - len(prompt)), 2)),
        )
        access_denied.addstr(1, 1, prompt, curses.A_BOLD | curses.color_pair(self.RED))
        access_denied.refresh()
        time.sleep(0.75)
        for index in range(0, 5):
            access_denied.addstr(1, 1, " " * len(prompt))
            access_denied.refresh()
            time.sleep(0.25)
            access_denied.addstr(
                1, 1, prompt, curses.A_BOLD | curses.color_pair(self.RED)
            )
            access_denied.refresh()
            time.sleep(0.75)
        self.stop()


###################
# > Main Entry
###################
def main(domain, port, secure, log_file, log_level):
    """ Creates and starts the monitor """
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter("\r[%(levelname)s] %(asctime)s - %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    lvl = LOG_LEVELS.get(log_level, "notset")
    logger.setLevel(lvl)
    enableTrace(True)
    if not secure:
        url = "ws://%s:%s%s" % (domain, port, __path__)
    else:
        url = "wss://%s:%s%s" % (domain, port, __path__)
    logging.info("Connecting to %s" % url)
    bot_monitor = BotMonitor(url)
    try:
        bot_monitor.start()
    except KeyboardInterrupt:
        bot_monitor.stop_thread = True
        time.sleep(0.2)
        os._exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Root the Box: Botnet Monitor")
    parser.add_argument(
        "--version", action="version", version="%(prog)s v" + __version__
    )
    parser.add_argument(
        "--secure",
        help="connect using a ssl (default: false)",
        action="store_true",
        dest="secure",
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
        help="network port to connect to (default: %s)" % __port__,
        default=__port__,
        dest="port",
    )
    parser.add_argument(
        "--log-file",
        "-f",
        help="log to file (default: %s)" % __log__,
        default=__log__,
        dest="log_file",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        help="log to file (default: notset)",
        default="notset",
        dest="log_level",
    )
    args = parser.parse_args()
    main(args.domain, args.port, args.secure, args.log_file, args.log_level.lower())
