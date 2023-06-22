# -*- coding: utf-8 -*-
"""
Created on Nov 24, 2014

@author: moloch

    Copyright 2014 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


Handlers related to controlling and configuring the overall game.
"""
# pylint: disable=unused-wildcard-import,no-member

import os
import subprocess
import logging
import defusedxml.minidom
import xml.etree.cElementTree as ET
import time

from tempfile import NamedTemporaryFile
from builtins import str
from models.Flag import Flag
from models.Box import Box
from models.Swat import Swat
from models.GameLevel import GameLevel
from models.User import ADMIN_PERMISSION
from models.Team import Team
from models.Theme import Theme
from models.Penalty import Penalty
from models.SourceCode import SourceCode
from models.Corporation import Corporation
from models.Category import Category
from models.Notification import Notification
from models.RegistrationToken import RegistrationToken
from models.EmailToken import EmailToken
from libs.EventManager import EventManager
from libs.SecurityDecorators import *
from libs.StringCoding import encode, decode
from libs.ValidationError import ValidationError
from libs.ConfigHelpers import save_config
from libs.ConsoleColors import *
from libs.Scoreboard import score_bots, Scoreboard
from handlers.BaseHandlers import BaseHandler
from string import printable
from setup.xmlsetup import import_xml
from tornado.options import options
from tornado.ioloop import PeriodicCallback
from past.builtins import basestring
from datetime import datetime


class AdminGameHandler(BaseHandler):

    """Start or stop the game"""

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        self.admin_actions(self)
        self.redirect("/user")

    @staticmethod
    def isOn(value):
        return value == "on" or value == "true"

    @staticmethod
    def admin_actions(self):
        start_game = self.get_argument("start_game", None)
        stop_game = self.get_argument("stop_game", None)
        suspend_reg = self.get_argument("suspend_registration", None)
        set_timer = self.get_argument("countdown_timer", None)
        hide_scoreboard = self.get_argument("hide_scoreboard", None)
        show_scoreboard = self.get_argument("show_scoreboard", None)
        stop_timer = self.get_argument("stop_timer", None)
        start_timer = self.get_argument("start_timer", None)

        if start_game is None and stop_game is not None:
            start_game = "false" if stop_game == "true" else "true"
        if stop_timer is None and start_timer is not None:
            stop_timer = "false" if start_timer == "true" else "true"
        if hide_scoreboard is None and show_scoreboard is not None:
            hide_scoreboard = "false" if show_scoreboard == "true" else "true"

        if (
            start_game
            and start_game != str(self.application.settings["game_started"]).lower()
        ):
            if self.get_argument("start_game", "") == "true":
                self.start_game()
            else:
                self.stop_game()
        if (
            stop_timer
            and self.isOn(stop_timer) != self.application.settings["stop_timer"]
        ):
            if self.isOn(stop_timer):
                self.application.settings["stop_timer"] = True
            else:
                self.application.settings["stop_timer"] = False
        if (
            suspend_reg
            and suspend_reg
            != str(self.application.settings["suspend_registration"]).lower()
        ):
            if suspend_reg == "true":
                self.application.settings["suspend_registration"] = True
            elif suspend_reg == "false":
                self.application.settings["suspend_registration"] = False
        if (
            hide_scoreboard
            and self.isOn(hide_scoreboard)
            != self.application.settings["hide_scoreboard"]
        ):
            if self.isOn(hide_scoreboard):
                self.application.settings["hide_scoreboard"] = True
            else:
                self.application.settings["hide_scoreboard"] = False
        if (
            set_timer
            and set_timer != str(self.application.settings["countdown_timer"]).lower()
        ):
            if set_timer == "false":
                self.application.settings["countdown_timer"] = False
                self.application.settings["stop_timer"] = False
                self.application.settings["hide_scoreboard"] = False
                if self.application.settings["temp_global_notifications"] is not None:
                    options.global_notification = self.application.settings[
                        "temp_global_notifications"
                    ]
                    self.application.settings["temp_global_notifications"] = None
                self.event_manager.push_scoreboard()
            elif set_timer:
                diff = 60 * int(float(set_timer))
                self.application.settings["countdown_timer"] = time.time() + diff
                self.application.settings[
                    "temp_global_notifications"
                ] = options.global_notification
                options.global_notification = False
                self.event_manager.push_scoreboard()
        return {
            "start_game": self.application.settings["game_started"],
            "suspend_registration": self.application.settings["suspend_registration"],
            "hide_scoreboard": self.application.settings["hide_scoreboard"],
            "countdown_timer": self.application.settings["countdown_timer"],
            "stop_timer": self.application.settings["stop_timer"],
        }


class AdminMessageHandler(BaseHandler):

    event_manager = EventManager.instance()

    """ Send a global notification message """

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        message = self.get_argument("message", "")
        if len(message) > 0:
            self.event_manager.admin_message(message)
            if self.chatsession:
                self.chatsession.post_message(message)
        self.redirect("/user")


class AdminRegTokenHandler(BaseHandler):

    """Manages registration tokens"""

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Call method based on URI"""
        uri = {"create": self.create, "view": self.view}
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """Used to delete regtokens"""
        token_value = self.get_argument("token_value", "")
        reg_token = RegistrationToken.by_value(token_value)
        if reg_token is not None:
            self.dbsession.delete(reg_token)
            self.dbsession.commit()
            self.redirect("/admin/regtoken/view")
        else:
            self.render("admin/view/token.html", errors=["Token does not exist"])

    def create(self):
        """Adds a registration token to the db and displays the value"""
        token = RegistrationToken()
        self.dbsession.add(token)
        self.dbsession.commit()
        self.render("admin/create/token.html", token=token)

    def view(self):
        """View all reg tokens"""
        self.render("admin/view/token.html", errors=None)


class AdminSourceCodeMarketHandler(BaseHandler):

    """Add source code files to the source code market"""

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render("admin/upgrades/source_code_market.html", errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {"/add": self.add_source_code, "/delete": self.delete_source_code}
        if len(args) and args[0] in uri:
            try:
                uri[args[0]]()
            except ValidationError as error:
                self.render(
                    "admin/upgrades/source_code_market.html", errors=[str(error)]
                )
        else:
            self.render("public/404.html")

    def add_source_code(self):
        box = Box.by_uuid(self.get_argument("box_uuid", ""))
        if box is not None:
            file_count = len(self.request.files["source_archive"])
            if "source_archive" not in self.request.files and 0 < file_count:
                raise ValidationError("No file data")
            else:
                price = self.get_argument("price", "")
                self.create_source_code(box, price)
                self.render("admin/upgrades/source_code_market.html", errors=None)
        else:
            raise ValidationError("The selected box does not exist")

    def create_source_code(self, box, price):
        """Save file data and create object in database"""
        description = self.get_argument("description", "")
        file_name = self.request.files["source_archive"][0]["filename"]
        source_code = SourceCode(
            file_name=file_name, box_id=box.id, price=price, description=description
        )
        self.dbsession.add(source_code)
        self.dbsession.flush()
        source_code.data = self.request.files["source_archive"][0]["body"]
        self.dbsession.add(source_code)
        self.dbsession.commit()

    def delete_source_code(self):
        """Delete source code file"""
        uuid = self.get_argument("box_uuid", "")
        box = Box.by_uuid(uuid)
        if box is not None and box.source_code is not None:
            box.source_code.delete_data()
            self.dbsession.delete(box.source_code)
            self.dbsession.commit()
        else:
            raise ValidationError("Box/source code does not exist")
        self.render("admin/upgrades/source_code_market.html", errors=None)


class AdminSwatHandler(BaseHandler):

    """Manage SWAT requests"""

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render_page()

    def render_page(self, errors=None):
        """Render page with extra arguments"""
        if errors is not None and not isinstance(errors, list):
            errors = [str(errors)]
        self.render(
            "admin/upgrades/swat.html",
            pending_bribes=Swat.all_pending(),
            in_progress_bribes=Swat.all_in_progress(),
            completed_bribes=Swat.all_completed(),
            errors=errors,
        )

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """Accept/Complete bribes"""
        uri = {"/accept": self.accept_bribe, "/complete": self.complete_bribe}
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def accept_bribe(self):
        """Accept bribe, and lock user's account"""
        swat = Swat.by_uuid(self.get_argument("uuid", ""))
        if swat is not None and not swat.completed:
            logging.info("Accepted SWAT with uuid: %s", swat.uuid)
            swat.accepted = True
            swat.target.locked = True
            self.dbsession.add(swat)
            self.dbsession.add(swat.target)
            self.dbsession.commit()
            self.render_page()
        else:
            logging.warning(
                "Invalid request to accept bribe with uuid: %r"
                % (self.get_argument("uuid", ""),)
            )
            self.render_page("Requested SWAT object does not exist")

    def complete_bribe(self):
        """Complete bribe and unlock user's account"""
        swat = Swat.by_uuid(self.get_argument("uuid", ""))
        if swat is not None and not swat.completed:
            logging.info("Completed SWAT with uuid: %s", swat.uuid)
            swat.completed = True
            swat.target.locked = False
            self.dbsession.add(swat)
            self.dbsession.add(swat.target)
            self.dbsession.commit()
            self.render_page()
        else:
            logging.warning(
                "Invalid request to complete bribe with uuid: %r"
                % (self.get_argument("uuid", ""),)
            )
            self.render_page("Requested SWAT object does not exist")


class AdminConfigurationHandler(BaseHandler):

    """Allows the admin to change some of the configuration options"""

    def get_int(self, name, default=0):
        try:
            return abs(int(self.get_argument(name, default)))
        except:
            return default

    def get_bool(self, name, default=""):
        if not isinstance(default, basestring):
            default = str(default).lower()
        return self.get_argument(name, default) == "true"

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render("admin/configuration.html", errors=[], config=self.config)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """
        Update configuration
        Disabled fields will not be send in the POST, so check for blank values
        """
        errors = None
        self.config.game_name = self.get_argument("game_name", "Root the Box")
        self.config.restrict_registration = self.get_bool(
            "restrict_registration", False
        )
        self.config.require_email = self.get_bool("require_email", True)
        self.config.validate_email = self.get_bool("validate_email", False)
        if self.config.validate_email and not len(options.mail_host) > 0:
            errors = [
                "Mail settings must be defined in the rootthebox.cfg to Validate Email."
            ]
            self.config.validate_email = False
        self.config.global_notification = self.get_bool("global_notification", True)
        self.config.hints_taken = self.get_bool("hints_taken", False)
        self.config.story_mode = self.get_bool("story_mode", False)
        try:
            self.config.rank_by = str(self.get_argument("rank_by", "money"))
        except:
            self.config.rank_by = bytes(self.get_argument("rank_by", "money"))
        self.config.scoreboard_visibility = str(
            self.get_argument("scoreboard_visibility", "public")
        )
        self.config.teams = self.get_bool("teams", True)
        self.config.public_teams = self.get_bool("public_teams")
        self.config.show_mvp = self.get_bool("show_mvp")
        self.config.mvp_max = self.get_int("mvp_max", 10)
        self.config.team_sharing = self.get_bool("team_sharing")
        self.config.dynamic_flag_value = self.get_bool("dynamic_flag_value", False)
        self.config.dynamic_flag_type = self.get_argument(
            "dynamic_flag_type", "decay_future"
        )
        self.config.max_flag_attempts = self.get_int("max_flag_attempts", 100)
        self.config.flag_value_decrease = self.get_int("flag_value_decrease")
        self.config.flag_value_minimum = self.get_int("flag_value_minimum", 1)
        self.config.penalize_flag_value = self.get_bool("penalize_flag_value", False)
        self.config.flag_penalty_cost = self.get_int("flag_penalty_cost")
        self.config.flag_stop_penalty = self.get_int("flag_stop_penalty")
        self.config.flag_start_penalty = self.get_int("flag_start_penalty")
        self.config.max_team_size = self.get_int("max_team_size")
        self.config.min_user_password_length = self.get_int(
            "min_user_password_length", 12
        )
        self.config.banking = self.get_bool("banking", True)
        self.config.max_password_length = self.get_int("max_password_length", 7)
        self.config.starting_team_money = self.get_int("starting_team_money", 500)
        self.config_bots()
        self.config.bot_reward = self.get_int("bot_reward", 50)
        self.config.use_black_market = self.get_bool("use_black_market", True)
        self.config.password_upgrade_cost = self.get_int("password_upgrade_cost", 1000)
        self.config.bribe_cost = self.get_int("bribe_cost", 2500)
        self.config.max_pastebin_size = self.get_int("max_pastebin_size", 4096)
        self.render("admin/configuration.html", errors=errors, config=self.config)

    def config_bots(self):
        """Updates bot config, and starts/stops the botnet callback"""
        self.config.use_bots = self.get_bool("use_bots", True)
        if (
            self.config.use_bots
            and not self.application.settings["score_bots_callback"]._running
        ):
            logging.info("Starting botnet callback function")
            self.application.settings["score_bots_callback"].start()
        elif self.application.settings["score_bots_callback"]._running:
            logging.info("Stopping botnet callback function")
            self.application.settings["score_bots_callback"].stop()

    def on_finish(self):
        save_config()


class AdminGarbageCfgHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Download a Box's garbage file"""
        box = Box.by_uuid(self.get_argument("uuid", ""))
        if box is not None:
            data = box.get_garbage_cfg()
            self.set_header("Content-Type", "text/plain")
            self.set_header(
                "Content-disposition",
                "attachment; filename=%s.garbage"
                % "".join(list(filter(lambda char: char in printable[:-38], box.name))),
            )
            self.set_header("Content-Length", len(data))
            self.write(data)


class AdminGitStatusHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Get the status of Git"""
        sp = subprocess.Popen(
            ["git", "fetch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = sp.communicate()
        if err:
            git = "RTB Updates: Git unable to connect to repository"
        else:
            sp = subprocess.Popen(
                ["git", "status", "-uno"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = sp.communicate()
            out = str(out)
            if "Your branch is behind" in out and "modified:" in out:
                git = "RTB Updates: Modified files (merge conflicts)"
            elif "Your branch is" in out:
                branch = out.split("\n")
                for line in branch:
                    if "Your branch is" in line:
                        git = "RTB Updates: " + line
                        break
            else:
                git = out
        if git is not None:
            self.set_header("Content-Type", "text/plain;charset=utf-8")
            self.set_header("Content-Length", len(git))
            self.write(git)
        self.finish()

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """Update RTB to the latest repository code."""
        os.system("git pull")
        """
        Shutdown the actual process and restart the service.
        """
        pid = os.getpid()
        print(INFO + "%s : Restarting the service (%i)..." % (self.current_time(), pid))
        self.finish()
        os.execl("./setup/restart.sh", "./setup/restart.sh")

    def current_time(self):
        """Nicely formatted current time as a string"""
        return str(datetime.now()).split(" ")[1].split(".")[0]


class AdminExportHandler(BaseHandler):

    API_VERSION = "1"

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Export to document formats"""
        self.render("admin/export.html", errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """Include the requests exports in the xml dom"""
        root = ET.Element("rootthebox")
        root.set("api", self.API_VERSION)
        if self.get_argument("game_config", "") == "true":
            self.export_game_config(root)
        if self.get_argument("game_objects", "") == "true":
            self.export_game_objects(root)
        xml_dom = defusedxml.minidom.parseString(ET.tostring(root))
        self.write_xml(xml_dom.toprettyxml())

    def write_xml(self, xml_doc):
        """Write XML document to page"""
        self.set_header("Content-Type", "text/xml")
        self.set_header(
            "Content-disposition",
            "attachment; filename=%s.xml"
            % (self.config.game_name.replace("\n", "").replace("\r", ""),),
        )
        self.set_header("Content-Length", len(encode(xml_doc, "utf-8")))
        self.write(encode(xml_doc, "utf-8"))
        self.finish()

    def export_game_config(self, root):
        """
        Exports the game configuration options to an XML doc.
        """
        game_elem = ET.SubElement(root, "configuration")
        game_list = options.group_dict("game")
        images = ["ctf_logo", "story_character", "scoreboard_right_image"]
        for key in game_list:
            value = game_list[key]
            if key in images and len(value) > 0:
                if os.path.isfile(value):
                    path = value
                elif os.path.isfile(os.path.join("files", value)):
                    path = os.path.join("files", value)
                elif value[0] == "/" and os.path.isfile(value[1:]):
                    path = value[1:]
                else:
                    continue
                with open(path, mode="rb") as logo:
                    data = logo.read()
                    ET.SubElement(game_elem, key).text = encode(data, "base64")
            elif isinstance(value, list):
                child = ET.Element(key)
                game_elem.append(child)
                for item in value:
                    ET.SubElement(child, "line").text = str(item)
            elif len(str(value)) > 0:
                ET.SubElement(game_elem, key).text = str(value)

    def export_game_objects(self, root):
        """
        Exports the game objects to an XML doc.
        For the record, I hate XML with a passion.
        """
        levels_elem = ET.SubElement(root, "gamelevels")
        levels_elem.set("count", "%s" % str(GameLevel.count()))
        for level in GameLevel.all()[1:]:
            level.to_xml(levels_elem)
        category_elem = ET.SubElement(root, "categories")
        category_elem.set("count", "%s" % str(Category.count()))
        for category in Category.all():
            category.to_xml(category_elem)
        corps_elem = ET.SubElement(root, "corporations")
        corps_elem.set("count", "%s" % str(Corporation.count()))
        for corp in Corporation.all():
            corp.to_xml(corps_elem)


class AdminImportXmlHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Import setup files"""
        self.render("admin/import.html", success=None, errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """
        Import XML file uploaded by the admin.
        """
        if "xml_file" in self.request.files:
            fxml = self._get_tmp_file()
            errors = []
            success = None
            if import_xml(fxml):
                success = "Successfully imported XML objects"
            else:
                errors.append("Failed to parse file correctly.")
            os.unlink(fxml)
            self.refresh_app_config()
            self.render("admin/import.html", success=success, errors=errors)
        else:
            self.render("admin/import.html", success=None, errors=["No file data."])

    def _get_tmp_file(self):
        """Creates a tmp file with the file data"""
        data = self.request.files["xml_file"][0]["body"]
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.write(data)
        tmp_file.close()
        return tmp_file.name

    def refresh_app_config(self):
        # Update default theme
        self.application.ui_modules["Theme"].theme = Theme.by_name(
            options.default_theme
        )

        # Callback functions  - updates and starts/stops the botnet callback
        self.application.settings["score_bots_callback"].stop()
        self.application.score_bots_callback = PeriodicCallback(
            score_bots, options.bot_reward_interval
        )
        if options.use_bots:
            logging.info("Starting botnet callback function")
            self.application.settings["score_bots_callback"].start()


class AdminResetHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Reset Game Information"""
        self.render("admin/reset.html", success=None, errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        success, errors = self.reset(self.dbsession)
        Scoreboard.update_gamestate(self)
        self.event_manager.push_score_update()
        self.flush_memcached()
        self.render("admin/reset.html", success=success, errors=errors)

    @staticmethod
    def reset(dbsession):
        """
        Reset the Game
        """
        errors = []
        success = None
        try:
            users = User.all_users()
            for user in users:
                user.money = 0
            teams = Team.all()
            for team in teams:
                team.game_history = []
                if options.banking:
                    team.set_score("start", options.starting_team_money)
                else:
                    team.set_score("start", 0)
                team.flags = []
                team.hints = []
                team.boxes = []
                team.items = []
                team.purchased_source_code = []
                level_0 = GameLevel.by_number(0)
                if not level_0:
                    level_0 = GameLevel.all()[0]
                team.game_levels = [level_0]
                dbsession.add(team)
            dbsession.commit()
            dbsession.flush()
            for team in teams:
                for paste in team.pastes:
                    dbsession.delete(paste)
                for shared_file in team.files:
                    shared_file.delete_data()
                    dbsession.delete(shared_file)
            dbsession.commit()
            dbsession.flush()
            Penalty.clear()
            Notification.clear()
            swats = Swat.all()
            for swat in swats:
                dbsession.delete(swat)
            dbsession.commit()
            tokens = EmailToken.all()
            if tokens is not None:
                for token in tokens:
                    dbsession.delete(token)
            dbsession.commit()
            flags = Flag.all()
            for flag in flags:
                # flag.value = flag.value allows a fallback to when original_value was used
                # Allows for the flag value to be reset if dynamic scoring was used
                # Can be removed after depreciation timeframe
                flag.value = flag.value
                dbsession.add(flag)
            dbsession.commit()
            dbsession.flush()
            success = "Successfully Reset Game"
            return (success, errors)
        except BaseException as e:
            errors.append("Failed to Reset Game")
            logging.error(str(e))
            return (None, errors)


class AdminResetDeleteHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        """Reset Game Information"""
        self.render("admin/reset.html", success=None, errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        success, errors = self.reset(self.dbsession)
        Scoreboard.update_gamestate(self)
        self.event_manager.push_score_update()
        self.flush_memcached()
        self.render("admin/reset.html", success=success, errors=errors)

    @staticmethod
    def reset(dbsession):
        """
        Reset the Game - Delete all teams
        """
        errors = []
        success = None
        try:
            users = User.all_users()
            teams = Team.all()
            for team in teams:
                for paste in team.pastes:
                    dbsession.delete(paste)
                for shared_file in team.files:
                    shared_file.delete_data()
                    dbsession.delete(shared_file)
            dbsession.commit()
            dbsession.flush()
            Penalty.clear()
            Notification.clear()
            swats = Swat.all()
            for swat in swats:
                dbsession.delete(swat)
            dbsession.commit()
            tokens = EmailToken.all()
            for token in tokens:
                dbsession.delete(token)
            dbsession.commit()
            for user in users:
                dbsession.delete(user)
            dbsession.commit()
            for team in teams:
                dbsession.delete(team)
            dbsession.commit()
            flags = Flag.all()
            for flag in flags:
                # flag.value = flag.value allows a fallback to when original_value was used
                # Allows for the flag value to be reset if dynamic scoring was used
                # Can be removed after depreciation timeframe
                flag.value = flag.value
                dbsession.add(flag)
            dbsession.commit()
            dbsession.flush()

            if options.teams:
                success = "Successfully Deleted Teams"
            else:
                success = "Successfully Deleted Players"
            return (success, errors)
        except BaseException as e:
            if options.teams:
                errors.append("Failed to Delete Teams")
            else:
                errors.append("Failed to Delete Players")
            logging.error(str(e))
            return (None, errors)
