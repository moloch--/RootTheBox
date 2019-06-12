# -*- coding: utf-8 -*-
"""
Created on Oct 04, 2012

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
----------------------------------------------------------------------------

This file contains handlers related to the scoreboard.

"""
# pylint: disable=no-member


import json
import logging

from tornado.websocket import WebSocketHandler
from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import use_black_market
from libs.GameHistory import GameHistory
from libs.Scoreboard import Scoreboard
from builtins import str
from models.Team import Team
from models.User import User
from models.Box import Box
from models.Category import Category
from models.WallOfSheep import WallOfSheep
from datetime import datetime, timedelta
from tornado.options import options


class ScoreboardDataSocketHandler(WebSocketHandler):
    """ Get Score data via websocket """

    connections = set()

    def initialize(self):
        self.last_message = datetime.now()

    def open(self):
        """ When we receive a new websocket connect """
        self.connections.add(self)
        if self.application.settings["freeze_scoreboard"]:
            self.write_message("pause")
        else:
            self.write_message(Scoreboard.now(self))

    def on_message(self, message):
        """ We ignore messages if there are more than 1 every 3 seconds """
        if self.application.settings["freeze_scoreboard"]:
            self.write_message("pause")
        elif datetime.now() - self.last_message > timedelta(seconds=3):
            self.last_message = datetime.now()
            self.write_message(Scoreboard.now(self))

    def on_close(self):
        """ Lost connection to client """
        try:
            self.connections.remove(self)
        except KeyError:
            logging.warn("[Web Socket] Connection has already been closed.")


class ScoreboardHandler(BaseHandler):
    """ Main summary page """

    def get(self, *args, **kargs):
        user = self.get_current_user()
        if scoreboard_visible(user):
            self.render("scoreboard/summary.html", timer=self.timer())
        elif not user:
            self.redirect("/login")
        else:
            self.render("public/404.html")


class ScoreboardAjaxHandler(BaseHandler):
    def get(self, *args, **kargs):
        """ Renders AJAX snippit based on URI """
        uri = {
            "summary": self.summary_table,
            "team": self.team_details,
            "skills": self.team_skills,
            "mvp": self.mvp_table,
            "timer": self.timediff,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def summary_table(self):
        """ Render the "leaderboard" snippit """
        self.render("scoreboard/summary_table.html", teams=Team.ranks())

    def mvp_table(self):
        """ Render the "leaderboard" snippit """
        self.render("scoreboard/mvp_table.html", users=User.ranks())

    def timediff(self):
        timer = self.timer()
        if timer:
            self.write(timer)
        else:
            self.finish()

    def team_details(self):
        """ Returns team details in JSON form """
        uuid = self.get_argument("uuid", "")
        team = Team.by_uuid(uuid)
        if team is not None:
            details = {"name": team.name, "game_levels": []}
            for lvl in team.levels:
                lvl_details = {
                    "number": lvl.number,
                    "captured": [flag.name for flag in team.level_flags(lvl.number)],
                    "total": len(lvl.flags),
                }
                details["game_levels"].append(lvl_details)
            self.write(details)
        else:
            self.write({"error": "Team does not exist"})
        self.finish()

    def team_skills(self):
        """ Returns team details in JSON form """
        uuid = self.get_argument("uuid", "")
        if uuid == "":
            user = self.get_current_user()
            if user:
                team = user.team
        else:
            team = Team.by_uuid(uuid)
        if team is not None:
            categories = Category.all()
            catlist = {}
            for cat in categories:
                catbox = Box.by_category(cat.id)
                if len(catbox) > 0:
                    catlist[int(cat.id)] = 0
            for flag in team.flags:
                box = flag.box
                if box and box.category_id is not None:
                    catlist[int(box.category_id)] += 1
            skillvalues = []
            for val in catlist:
                skillvalues.append(catlist[val])
            self.write(str(skillvalues))
        else:
            self.write({"error": "Team does not exist"})
        self.finish()


class ScoreboardHistoryHandler(BaseHandler):
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        if scoreboard_visible(user):
            self.render("scoreboard/history.html", timer=self.timer())
        elif not user:
            self.redirect("/login")
        else:
            self.render("public/404.html")


class ScoreboardHistorySocketHandler(WebSocketHandler):

    connections = set()
    game_history = GameHistory.instance()

    def initialize(self):
        self.last_message = datetime.now()

    def open(self):
        """ When we receive a new websocket connect """
        self.connections.add(self)
        history_length = int(self.get_argument("length", 29))
        self.write_message(self.get_history(history_length))

    def on_message(self, message):
        """ We ignore messages if there are more than 1 every 3 seconds """
        if self.application.settings["freeze_scoreboard"]:
            self.write_message("pause")
        elif datetime.now() - self.last_message > timedelta(seconds=3):
            self.last_message = datetime.now()
            self.write_message(self.get_history(1))

    def on_close(self):
        """ Lost connection to client """
        self.connections.remove(self)

    def get_history(self, length=29):
        """ Send history in JSON """
        length = abs(length) + 1
        return json.dumps({"history": self.game_history[(-1 * length) :]})


class ScoreboardWallOfSheepHandler(BaseHandler):
    @use_black_market
    def get(self, *args, **kwargs):
        """ Optionally order by argument; defaults to date/time """
        user = self.get_current_user()
        if scoreboard_visible(user):
            order = self.get_argument("order_by", "").lower()
            if order == "prize":
                sheep = WallOfSheep.all_order_value()
            elif order == "length":
                sheep = sorted(WallOfSheep.all())
            else:
                sheep = WallOfSheep.all_order_created()
            leaderboard = WallOfSheep.leaderboard()
            self.render(
                "scoreboard/wall_of_sheep.html", leaderboard=leaderboard, flock=sheep
            )
        elif not user:
            self.redirect("/login")
        else:
            self.render("public/404.html")


class ScoreboardPauseHandler(WebSocketHandler):

    connections = set()

    def open(self):
        """ When we receive a new websocket connect """
        self.connections.add(self)
        if self.application.settings["freeze_scoreboard"]:
            self.write_message("pause")
        else:
            self.write_message("play")

    def on_message(self, message):
        if self.application.settings["freeze_scoreboard"]:
            self.write_message("pause")
        else:
            self.write_message("play")

    def on_close(self):
        """ Lost connection to client """
        try:
            self.connections.remove(self)
        except KeyError:
            logging.warn("[Web Socket] Connection has already been closed.")


class TeamsHandler(BaseHandler):
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        if scoreboard_visible(user):
            self.render("scoreboard/teams.html", timer=self.timer())
        elif not user:
            self.redirect("/login")
        else:
            self.render("public/404.html")


def scoreboard_visible(user):
    if options.scoreboard_visibility == "public":
        return True
    if user:
        return options.scoreboard_visibility == "players" or user.is_admin()
    return False
