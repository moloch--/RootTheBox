# -*- coding: utf-8 -*-
"""
Created on Sep 25, 2012

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

This file contains the "Upgrade Handlers", access to these handlers can
be purchased from the "Black Market" (see markethandlers.py)

"""


import logging

from .BaseHandlers import BaseHandler
from models.WallOfSheep import WallOfSheep
from models.Team import Team
from models.Box import Box
from models.SourceCode import SourceCode
from models.Swat import Swat
from models.User import User
from libs.SecurityDecorators import (
    authenticated,
    item_allowed,
    has_item,
    use_black_market,
    game_started,
)
from builtins import str
from mimetypes import guess_type
from base64 import b64decode
from string import ascii_letters


class PasswordSecurityHandler(BaseHandler):
    """Renders views of items in the market"""

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Password Security")
    @has_item("Password Security")
    def get(self, *args, **kwargs):
        """Render update hash page"""
        self.render_page()

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Password Security")
    @has_item("Password Security")
    def post(self, *args, **kwargs):
        """Attempt to upgrade hash algo"""
        user = self.get_current_user()
        passwd = self.get_argument("new_password1", "")
        old_passwd = self.get_argument("old_password", "")
        if not user.validate_bank_password(old_passwd):
            self.render_page(["Invalid password"])
        elif not passwd == self.get_argument("new_password2", None):
            self.render_page(["New passwords do not match"])
        elif user.team.money < self.config.password_upgrade_cost:
            self.render_page(["You cannot afford to upgrade your hash"])
        elif len(passwd) <= self.config.max_password_length:
            user.team.money -= self.config.password_upgrade_cost
            self.dbsession.add(user.team)
            self.dbsession.commit()
            self.event_manager.push_score_update()
            self.update_password(passwd)
            self.render_page()
        else:
            self.render_page(["New password is too long"])

    def render_page(self, errors=None):
        user = self.get_current_user()
        self.render(
            "upgrades/password_security.html",
            errors=errors,
            user=user,
            cost=self.config.password_upgrade_cost,
        )

    def update_password(self, new_password):
        """
        Update user to new hashing algorithm and then updates the password
        using the the new algorithm
        """
        user = self.get_current_user()
        next_algorithm = user.next_algorithm()
        user.algorithm = next_algorithm[2]  # String
        self.dbsession.add(user)
        self.dbsession.flush()
        user.bank_password = new_password
        self.dbsession.add(user)
        self.dbsession.commit()


class FederalReserveHandler(BaseHandler):
    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Federal Reserve")
    @has_item("Federal Reserve")
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        # CSP problem & use of console commands.
        # TODO: Fix Terminal.js so that this is no longer needed.
        self.add_content_policy("script-src", "'unsafe-eval'")
        self.render("upgrades/federal_reserve.html", user=user)


class FederalReserveAjaxHandler(BaseHandler):
    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Federal Reserve")
    @has_item("Federal Reserve")
    def get(self, *args, **kwargs):
        commands = {
            "ls": self.ls,  # Query
            "info": self.info,  # Report
            "xfer": self.transfer,  # Transfer
        }
        if 0 < len(args) and args[0] in commands:
            commands[args[0]]()
        else:
            self.write({"error": "No argument"})
            self.finish()

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Federal Reserve")
    @has_item("Federal Reserve")
    def post(self, *args, **kwargs):
        self.get(*args, **kwargs)

    def ls(self):
        current_user = self.get_current_user()
        if self.get_argument("data", "").lower() == "accounts":
            data = {}
            for team in Team.all():
                if team == current_user.team:
                    continue
                else:
                    data[team.name] = {
                        "money": team.money,
                        "flags": len(team.flags),
                        "bots": team.bot_count,
                    }
            self.write({"accounts": data})
        elif self.get_argument("data", "").lower() == "users":
            data = {}
            target_users = User.not_team(current_user.team.id)
            for user in target_users:
                data[user.handle] = {
                    "account": user.team.name,
                    "algorithm": user.algorithm,
                    "password": user.bank_password,
                }
            self.write({"users": data})
        else:
            self.write({"Error": "Invalid data type"})
        self.finish()

    def info(self):
        team_name = self.get_argument("account", "")
        team = Team.by_name(team_name)
        if team is not None:
            self.write(
                {
                    "name": team.name,
                    "balance": team.money,
                    "users": [user.handle for user in team.members],
                }
            )
        else:
            self.write({"error": "Account does not exist"})
        self.finish()

    def transfer(self):
        user = self.get_current_user()
        source = Team.by_name(self.get_argument("source", ""))
        destination = Team.by_name(self.get_argument("destination", ""))
        try:
            amount = int(self.get_argument("amount", 0))
        except ValueError:
            amount = 0
        victim_user = User.by_handle(self.get_argument("user", None))
        password = self.get_argument("password", "")
        user = self.get_current_user()
        # Validate what we got from the user
        if source is None:
            self.write({"error": "Source account does not exist"})
        elif destination is None:
            self.write({"error": "Destination account does not exist"})
        elif victim_user is None or victim_user not in source.members:
            self.write({"error": "User is not authorized for this account"})
        elif victim_user in user.team.members:
            self.write({"error": "You cannot steal from your own team"})
        elif not 0 < amount <= source.money:
            self.write(
                {
                    "error": "Invalid transfer amount; must be greater than 0 and less than $%d"
                    % source.money
                }
            )
        elif destination == source:
            self.write({"error": "Source and destination are the same account"})
        elif victim_user.validate_bank_password(password):
            logging.info(
                "Transfer request from %s to %s for $%d by %s"
                % (source.name, destination.name, amount, user.handle)
            )
            xfer = self.theft(victim_user, destination, amount, password)
            self.write(
                {
                    "success": "Confirmed transfer to '%s' for $%d (15%s commission)"
                    % (destination.name, xfer, "%")
                }
            )
        else:
            self.write({"error": "Incorrect password for account, try again"})
        self.finish()

    def theft(self, victim, destination, amount, preimage):
        """Successfully cracked a password"""
        victim.team.money -= abs(amount)
        value = int(abs(amount) * 0.85)
        destination.money += value
        self.dbsession.add(destination)
        self.dbsession.add(victim.team)
        user = self.get_current_user()
        sheep = WallOfSheep(
            preimage=str(preimage), cracker_id=user.id, victim_id=victim.id, value=value
        )
        self.dbsession.add(sheep)
        self.dbsession.commit()
        self.event_manager.cracked_password(user, victim, preimage, value)
        return value


class SourceCodeMarketHandler(BaseHandler):
    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Source Code Market")
    @has_item("Source Code Market")
    def get(self, *args, **kwargs):
        self.render_page()

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Source Code Market")
    @has_item("Source Code Market")
    def post(self, *args, **kwargs):
        box = Box.by_uuid(self.get_argument("box_uuid", ""))
        if box is not None and box.source_code is not None:
            user = self.get_current_user()
            if box.source_code.price <= user.team.money:
                self.purchase_code(box)
                self.redirect("/source_code_market")
            else:
                self.render_page(["You cannot afford to purchase this code"])
        else:
            self.render_page(["Box does not exist"])

    def purchase_code(self, box):
        """Modify the database to reflect purchase"""
        team = self.get_current_user().team
        source_code = SourceCode.by_box_id(box.id)
        team.money -= abs(source_code.price)
        team.purchased_source_code.append(source_code)
        logging.info(
            "%s purchased '%s' from the source code market."
            % (team.name, source_code.file_name)
        )
        self.dbsession.add(team)
        self.dbsession.commit()
        self.event_manager.push_score_update()

    def render_page(self, errors=None):
        """Adds extra params to render()"""
        user = self.get_current_user()
        boxes = [box for box in sorted(Box.all()) if box.source_code is not None]
        self.render(
            "upgrades/source_code_market.html", user=user, boxes=boxes, errors=errors
        )


class SourceCodeMarketDownloadHandler(BaseHandler):
    """Allows users to download files they have purchased"""

    goodchars = ascii_letters + "1234567890-._"

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("Source Code Market")
    @has_item("Source Code Market")
    def get(self, *args, **kwargs):
        """Send file to user if their team owns it"""
        uuid = self.get_argument("uuid", "")
        box = Box.by_uuid(uuid)
        if box is not None and box.source_code is not None:
            user = self.get_current_user()
            if box.source_code in user.team.purchased_source_code:
                content_type = guess_type(box.source_code.file_name)[0]
                if content_type is None:
                    content_type = "unknown/data"
                self.set_header("Content-Type", content_type)
                self.set_header("Content-Length", len(box.source_code.data))
                fname = "".join(
                    [
                        char
                        for char in box.source_code.file_name
                        if char in self.goodchars
                    ]
                )
                self.set_header(
                    "Content-Disposition", "attachment; filename=%s" % fname
                )
                self.write(box.source_code.data)
                self.finish()
            else:
                self.render("public/404.html")
        else:
            self.render("public/404.html")


class SwatHandler(BaseHandler):
    """Allows users to bribe "police" to SWAT other players"""

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("SWAT")
    @has_item("SWAT")
    def get(self, *args, **kwargs):
        """Render SWAT page"""
        self.render_page()

    @authenticated
    @use_black_market
    @game_started
    @item_allowed("SWAT")
    @has_item("SWAT")
    def post(self, *args, **kwargs):
        """Validate user arguments for SWAT request"""
        target = User.by_uuid(self.get_argument("uuid", ""))
        if target is not None and not target.is_admin():
            if not Swat.user_is_pending(target) and not Swat.user_is_in_progress(
                target
            ):
                user = self.get_current_user()
                if target not in user.team.members:
                    if Swat.get_price(target) <= user.team.money:
                        self.create_swat(user, target)
                        self.redirect("/swat")
                    else:
                        self.render_page("You cannot afford this bribe")
                else:
                    self.render_page("You cannot SWAT your own team")
            else:
                self.render_page("A bribe is already exists for this player")
        else:
            self.render_page("Target user does not exist")

    def create_swat(self, user, target):
        """Create Swat request object in database"""
        price = Swat.get_price(target)
        assert 0 < price
        user.team.money -= price
        swat = Swat(user_id=user.id, target_id=target.id, paid=price)
        self.dbsession.add(swat)
        self.dbsession.add(user.team)
        self.dbsession.commit()
        self.event_manager.push_score_update()

    def render_page(self, errors=None):
        """Render page with extra arguments"""
        if errors is not None and not isinstance(errors, list):
            errors = [str(errors)]
        user = self.get_current_user()
        targets = [
            target for target in User.all_users() if target not in user.team.members
        ]
        self.render(
            "upgrades/swat.html",
            targets=targets,
            user_bribes=Swat.ordered_by_user_id(user.id),
            errors=None,
        )
