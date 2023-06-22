# -*- coding: utf-8 -*-
"""
Created on Mar 15, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
# pylint: disable=unused-wildcard-import,no-member


import os
import json
import logging
import tornado.websocket
import binascii


from uuid import uuid4
from hashlib import sha512
from libs.BotManager import BotManager
from libs.EventManager import EventManager
from libs.StringCoding import encode, decode
from builtins import str
from models import Box, Team, User
from .BaseHandlers import BaseHandler, BaseWebSocketHandler
from libs.SecurityDecorators import *
from tornado.options import options


class BotSocketHandler(tornado.websocket.WebSocketHandler):
    """
    *** Rough bot protocol layout ***
    =================================
    1) Bot connects to server
        a) If IP config.whitelist_box_ips is enabled, check
           the database for boxes with matching IPs

    2) Server responds with "Interrogation" request
        a) This request includes a random string 'xid'

    3) Bot responds with a "InterrogationResponse", includes
        a) The value of SHA512(SHA512(xid + garbage))
        b) Asserted user handle (reward goes to user.team)
        c) Asserted box name

    4) Server looks up asserted box and user in database, ensures
       they do exist, and the user is not an admin.

    5) Server then computes it's own SHA512(SHA512(xid + box garbage))
        a) Check if the server's value matches the bot's

    6) Check for duplicate bots (one bot per box per team)

    7) Add new bot to botnet

    """

    bot_manager = BotManager.instance()
    event_manager = EventManager.instance()
    config = options
    team_name = None
    team_uuid = None
    box_uuid = None
    remote_ip = None

    def initialize(self):
        try:
            hex_random = os.urandom(16).hex()
        except AttributeError:
            hex_random = binascii.hexlify(os.urandom(16)).decode()
        self.xid = hex_random
        if not self.config.use_bots:
            self.close()
        else:
            self.uuid = str(uuid4())
            self.opcodes = {"interrogation_response": self.interrogation_response}

    def open(self, *args):
        """Steps 1 and 2; called when a new bot connects"""
        box = Box.by_ip_address(self.request.remote_ip)
        self.remote_ip = self.request.remote_ip
        if box is None and self.config.whitelist_box_ips:
            logging.debug("Rejected bot from '%s' (not a box)" % self.request.remote_ip)
            self.write_message({"opcode": "error", "message": "Invalid IP address."})
            self.close()
        else:
            logging.debug("Interrogating bot on %s" % self.request.remote_ip)
            self.write_message({"opcode": "interrogate", "xid": str(self.xid)})

    def on_message(self, message):
        """Routes the request to the correct function based on opcode"""
        try:
            req = json.loads(message)
            if "opcode" not in req:
                raise ValueError("Missing opcode")
            elif req["opcode"] not in self.opcodes:
                raise ValueError("Invalid opcode in request: %s" % req["opcode"])
            else:
                self.opcodes[req["opcode"]](req)
        except ValueError as error:
            logging.warning("Invalid json request from bot: %s" % str(error))
            self.close()

    def on_close(self):
        """Close connection to remote host"""
        if self.uuid in self.bot_manager.botnet:
            self.bot_manager.remove_bot(self)
        logging.debug("Closing connection to bot at %s" % self.request.remote_ip)

    def interrogation_response(self, msg):
        """Steps 3 and 4; validate responses"""
        logging.debug("Received interrogate response, validating ...")
        response_xid = msg["response_xid"]
        user = User.by_handle(msg["handle"])
        box = Box.by_name(msg["box_name"])
        if self.config.whitelist_box_ips and self.remote_ip not in box.ips:
            self.send_error("Invalid remote IP for this box")
        elif user is None or user.is_admin():
            self.send_error("User does not exist")
        elif box is None:
            self.send_error("Box does not exist")
        elif not self.is_valid_xid(box, response_xid):
            self.send_error("Invalid xid response")
        else:
            self.team_name = user.team.name
            self.team_uuid = user.team.uuid
            self.box_uuid = box.uuid
            self.box_name = box.name
            self.add_to_botnet(user)

    def add_to_botnet(self, user):
        """Step 6 and 7; Add current web socket to botnet"""
        if self.bot_manager.add_bot(self):
            logging.debug("Auth okay, adding '%s' to botnet" % self.uuid)
            count = self.bot_manager.count_by_team(self.team_name)
            self.write_message(
                {
                    "opcode": "status",
                    "message": "Added new bot; total number of bots is now %d" % count,
                }
            )
            self.event_manager.bot_added(user, count)
        else:
            logging.debug("Duplicate bot on %s" % self.remote_ip)
            self.send_error("Duplicate bot")

    def is_valid_xid(self, box, response_xid):
        round1 = encode(sha512(encode(self.xid + box.garbage)).hexdigest())
        return response_xid == sha512(round1).hexdigest()

    def ping(self):
        """Just make sure we can write data to the socket"""
        try:
            self.write_message({"opcode": "ping"})
        except:
            logging.exception("Error: while sending ping to bot.")
            self.close()

    def send_error(self, msg):
        """Send the errors, and close socket"""
        self.write_message({"opcode": "error", "message": msg})
        self.close()


class BotCliMonitorSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Handles the CLI BotMonitor websocket connections, has custom auth.
    TODO: Trash this and use the web api handler, w/ normal session cookie
    """

    config = options
    bot_manager = BotManager.instance()
    team_name = None

    def initialize(self):
        if not self.config.use_bots:
            self.close()
        else:
            self.uuid = str(uuid4())
            self.opcodes = {"auth": self.auth}

    def open(self):
        logging.debug("Opened new monitor socket to %s" % self.request.remote_ip)

    def on_message(self, message):
        """Parse request"""
        try:
            req = json.loads(message)
            if "opcode" not in req:
                raise ValueError("Missing opcode")
            elif req["opcode"] not in self.opcodes:
                raise ValueError("Invalid opcode in request: %s" % req["opcode"])
            else:
                self.opcodes[req["opcode"]](req)
        except ValueError as error:
            logging.warning("Invalid json request from bot: %s" % str(error))

    def on_close(self):
        """Close connection to remote host"""
        self.bot_manager.remove_monitor(self)
        logging.debug(
            "Closing connection to bot monitor at %s" % self.request.remote_ip
        )

    def auth(self, req):
        """Authenticate user"""
        try:
            user = User.by_handle(req["handle"])
        except:
            user = None
        if user is None or user.is_admin():
            logging.debug("Monitor socket user does not exist.")
            self.write_message(
                {"opcode": "auth_failure", "message": "Authentication failure"}
            )
            self.close()
        elif user.validate_password(req.get("password", "")):
            logging.debug(
                "Monitor socket successfully authenticated as %s" % user.handle
            )
            self.team_name = "".join(user.team.name)
            self.bot_manager.add_monitor(self)
            self.write_message({"opcode": "auth_success"})
            bots = self.bot_manager.get_bots(self.team_name)
            self.update(bots)
        else:
            logging.debug("Monitor socket provided invalid password for user")
            self.write_message(
                {"opcode": "auth_failure", "message": "Authentication failure"}
            )
            self.close()

    def update(self, bots):
        """Called by the observable class"""
        self.write_message({"opcode": "update", "bots": bots})

    def ping(self):
        self.write_message({"opcode": "ping"})


class BotWebMonitorHandler(BaseHandler):
    """Just renders the html page for the web monitor"""

    @authenticated
    @use_bots
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        self.render("botnet/monitor.html", teamname=user.is_admin())


class BotWebMonitorSocketHandler(BaseWebSocketHandler):
    """
    Bot monitor API, requires user to be authenticated with the web app
    TODO: Move the cli api to use this one.

    This class implements an observer pattern, and registers itself with
    the BotManager class.

    It must have:
        cls.uuid
        cls.team_name
        cls.ping

    """

    def initialize(self):
        self.config = options
        if not self.config.use_bots:
            self.close()

    def open(self):
        """Only open sockets from authenticated clients"""
        user = self.get_current_user()
        if self.session is not None and ("team_id" in self.session or user.is_admin()):
            logging.debug(
                "[Web Socket] Opened web monitor socket with %s" % user.handle
            )
            self.uuid = str(uuid4())
            self.bot_manager = BotManager.instance()

            if user.is_admin():
                self.team_name = user.name
                self.bot_manager.add_monitor(self)
                bots = self.bot_manager.get_all_bots()
            else:
                self.team_name = "".join(user.team.name)
                self.bot_manager.add_monitor(self)
                bots = self.bot_manager.get_bots(self.team_name)
            self.update(bots)
        else:
            logging.debug(
                "[Web Socket] Denied web monitor socket to %s" % self.request.remote_ip
            )
            self.bot_manager = None
            self.close()

    def on_message(self, message):
        user = self.get_current_user()
        logging.debug("%s is send us websocket messages." % user.handle)

    def update(self, boxes):
        """Called by observable class"""
        self.write_message({"opcode": "update", "bots": boxes})

    def ping(self):
        """Send an update as a ping"""
        bots = self.bot_manager.get_bots(self.team_name)
        self.update(bots)

    def on_close(self):
        """Close connection to remote host"""
        if self.bot_manager is not None:
            self.bot_manager.remove_monitor(self)


class BotDownloadHandler(BaseHandler):
    """Distributes bot binaries / scripts"""

    @authenticated
    @use_bots
    def get(self, *args, **kwargs):
        download_options = {
            "windows": self.windows,
            "linux": self.generic,
            "monitor": self.monitor,
        }
        if len(args) and args[0] in download_options:
            download_options[args[0]]()
        self.finish()

    def windows(self):
        """Download Windows PE file"""
        self.set_header("Content-Type", "application/exe")
        self.set_header("Content-disposition", "attachment; filename=rtb_bot.exe")
        if os.path.exists("bot/dist/bot.exe"):
            with open("bot/dist/bot.exe", "rb") as fp:
                data = fp.read()
                self.set_header("Content-Length", len(data))
                self.write(data)
        else:
            logging.error(
                "Missing Windows bot file, please run build script: bot/build_bot.py"
            )
            self.generic()

    def generic(self):
        """Send them the generic python script"""
        self.set_header("Content-Type", "text/x-python")
        self.set_header("Content-disposition", "attachment; filename=rtb_bot.py")
        if os.path.exists("bot/bot.py"):
            with open("bot/bot.py", "rb") as fp:
                data = fp.read()
                self.set_header("Content-Length", len(data))
                self.write(data)

    def monitor(self):
        """Send curses ui bot monitor"""
        self.set_header("Content-Type", "text/x-python")
        self.set_header("Content-disposition", "attachment; filename=botnet_monitor.py")
        if os.path.exists("bot/BotMonitor.py"):
            with open("bot/BotMonitor.py", "rb") as fp:
                data = fp.read()
                self.set_header("Content-Length", len(data))
                self.write(data)
