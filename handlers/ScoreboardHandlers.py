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
from libs.SecurityDecorators import use_black_market, item_allowed
from libs.GameHistory import GameHistory
from libs.Scoreboard import Scoreboard
from builtins import str
from math import ceil
from models.Team import Team
from models.User import User
from models.Box import Box
from models.Category import Category
from models.WallOfSheep import WallOfSheep
from datetime import datetime, timedelta
from tornado.options import options
from collections import OrderedDict


class ScoreboardDataSocketHandler(WebSocketHandler):
    """Get Score data via websocket"""

    connections = set()

    def initialize(self):
        self.last_message = datetime.now()

    def open(self):
        """When we receive a new websocket connect"""
        self.connections.add(self)
        if self.application.settings["hide_scoreboard"]:
            self.write_message("pause")
        else:
            self.write_message(Scoreboard.now(self))

    def on_message(self, message):
        """We ignore messages if there are more than 1 every 3 seconds"""
        Scoreboard.update_gamestate(self)
        if self.application.settings["hide_scoreboard"]:
            self.write_message("pause")
        elif datetime.now() - self.last_message > timedelta(seconds=3):
            self.last_message = datetime.now()
            self.write_message(Scoreboard.now(self))

    def on_close(self):
        """Lost connection to client"""
        try:
            self.connections.remove(self)
        except KeyError:
            logging.warning("[Web Socket] Connection has already been closed.")


class ScoreboardHandler(BaseHandler):
    """Main summary page"""

    def get(self, *args, **kargs):
        user = self.get_current_user()
        try:
            page = int(self.get_argument("page", 0))
            display = int(self.get_argument("count", 50))
        except ValueError:
            page = 1
            display = 50
        if scoreboard_visible(user):
            if not options.scoreboard_lazy_update:
                Scoreboard.update_gamestate(self)
            settings = self.application.settings
            teamcount = len(settings["scoreboard_state"].get("teams"))
            if page == 0:
                page = 1
                if teamcount > display and user and user.team:
                    # Jump to the user's place in the scoreboard
                    for index, team in enumerate(
                        settings["scoreboard_state"].get("teams"), start=1
                    ):
                        if user.team.name == team:
                            page = max(1, ceil(index / display))
                            break

            self.render(
                "scoreboard/summary.html",
                timer=self.timer(),
                hide_scoreboard=settings["hide_scoreboard"],
                page=page,
                display=display,
                teamcount=teamcount,
            )
        elif not user:
            self.redirect("/login")
        else:
            self.render("public/404.html")


class ScoreboardAjaxHandler(BaseHandler):
    def get(self, *args, **kargs):
        """Renders AJAX snippit based on URI"""
        uri = {
            "summary": self.summary_table,
            "team": self.team_details,
            "skills": self.team_skills,
            "mvp": self.mvp_table,
            "timer": self.timediff,
            "feed": self.json_feed,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def json_feed(self):
        """Render the "leaderboard" json feed - CTFtime: https://ctftime.org/json-scoreboard-feed"""
        self.set_header("Content-Type", "application/json")
        feed = {}
        user = self.get_current_user()
        if options.scoreboard_visibility == "public" or user.is_admin():
            feed["standings"] = []
            teams = self.settings["scoreboard_state"]["teams"]
            for index, team in enumerate(teams):
                feed["standings"].append(
                    {"pos": index + 1, "team": team, "score": teams[team].get("money")}
                )
        else:
            feed["error"] = "scoreboard is not set to public."
        self.write(json.dumps(feed, sort_keys=True, indent=4))

    def summary_table(self):
        """Render the "leaderboard" team snippit"""
        try:
            page = int(self.get_argument("page", 1))
            display = int(self.get_argument("count", 50))
        except ValueError:
            page = 1
            display = 50
        self.render(
            "scoreboard/summary_table.html",
            game_state=self.summary_page(page, display),
            page=page,
            display=display,
        )

    def summary_page(self, page, display):
        """Prepare the pagination for the leaderboard"""
        teams = self.settings["scoreboard_state"].get("teams")
        teamcount = len(teams)
        if teamcount > display:
            scoreboard = self.settings["scoreboard_state"].copy()
            scoreboard["teams"] = OrderedDict()
            end_count = display * page
            start_count = end_count - display
            for i, team in enumerate(teams):
                if i >= start_count and i < end_count:
                    scoreboard["teams"][team] = teams[team]
                elif i >= end_count:
                    break
            return scoreboard
        else:
            return self.settings["scoreboard_state"]

    def mvp_table(self):
        """Render the "leaderboard" mvp snippit"""
        users = self.settings["scoreboard_state"].get("users")
        self.render("scoreboard/mvp_table.html", users=users)

    def timediff(self):
        timer = self.timer()
        if timer:
            self.write(timer)
        else:
            self.finish()

    def team_details(self):
        """Returns team details in JSON form"""
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
        """Returns team details in JSON form"""
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
            self.render(
                "scoreboard/history.html",
                hide_scoreboard=self.application.settings["hide_scoreboard"],
                timer=self.timer(),
            )
        elif not user:
            self.redirect("/login")
        else:
            self.render("public/404.html")


class ScoreboardFeedHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """Renders the scoreboard feed page"""
        hostname = "%s://%s" % (self.request.protocol, self.request.host)
        self.render("scoreboard/feed.html", hostname=hostname)


class ScoreboardHistorySocketHandler(WebSocketHandler):

    connections = set()
    game_history = GameHistory.instance()

    def initialize(self):
        self.game_history._load()
        self.last_message = datetime.now()

    def open(self):
        """When we receive a new websocket connect"""
        self.connections.add(self)
        history_length = int(self.get_argument("length", 29))
        self.write_message(self.get_history(history_length))

    def on_message(self, message):
        """We ignore messages if there are more than 1 every 3 seconds"""
        if self.application.settings["hide_scoreboard"]:
            self.write_message("pause")
        elif datetime.now() - self.last_message > timedelta(seconds=3):
            self.last_message = datetime.now()
            self.write_message(self.get_history(1))

    def on_close(self):
        """Lost connection to client"""
        self.connections.remove(self)

    def get_history(self, length=29):
        """Send history in JSON"""
        length = abs(length) + 1
        return json.dumps({"history": self.game_history[(-1 * length) :]})


class ScoreboardWallOfSheepHandler(BaseHandler):
    @use_black_market
    @item_allowed("Federal Reserve")
    def get(self, *args, **kwargs):
        """Optionally order by argument; defaults to date/time"""
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
        """When we receive a new websocket connect"""
        self.connections.add(self)
        if self.application.settings["hide_scoreboard"]:
            self.write_message("pause")
        else:
            self.write_message("play")

    def on_message(self, message):
        if self.application.settings["hide_scoreboard"]:
            self.write_message("pause")
        else:
            self.write_message("play")

    def on_close(self):
        """Lost connection to client"""
        try:
            self.connections.remove(self)
        except KeyError:
            logging.warning("[Web Socket] Connection has already been closed.")


class TeamsHandler(BaseHandler):
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        try:
            page = int(self.get_argument("page", 1))
            display = int(self.get_argument("count", 25))
        except ValueError:
            page = 1
            display = 25
        ranks = self.application.settings["scoreboard_state"]["teams"]
        teamcount = len(ranks)
        pcount = int(ceil(teamcount / float(display)))
        if pcount < page:
            page = pcount
        end_count = display * page
        start_count = end_count - display
        teams = []
        for i, team in enumerate(ranks):
            if i >= start_count and i < end_count:
                teams.append(Team.by_uuid(ranks[team].get("uuid")))
            elif i >= end_count:
                break

        if scoreboard_visible(user):
            self.render(
                "scoreboard/teams.html",
                timer=self.timer(),
                hide_scoreboard=self.application.settings["hide_scoreboard"],
                teams=teams,
                page=page,
                display=display,
                teamcount=teamcount,
            )
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
