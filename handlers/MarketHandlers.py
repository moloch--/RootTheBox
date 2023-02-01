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

This file contains handlers related to the "Black Market" functionality

"""


import logging

from tornado.options import options
from .BaseHandlers import BaseHandler
from models.MarketItem import MarketItem
from models.Team import Team
from libs.SecurityDecorators import authenticated, use_black_market, game_started


class MarketViewHandler(BaseHandler):

    """Renders views of items in the market"""

    @authenticated
    @game_started
    @use_black_market
    def get(self, *args, **kwargs):
        """Renders the main table"""
        user = self.get_current_user()
        self.render("market/view.html", user=user, errors=None)

    @authenticated
    @game_started
    @use_black_market
    def post(self, *args, **kwargs):
        """Called to purchase an item"""
        uuid = self.get_argument("uuid", "")
        item = MarketItem.by_uuid(uuid)
        if item is not None:
            user = self.get_current_user()
            team = Team.by_id(user.team.id)  # Refresh object
            if item.name not in options.allowed_market_items:
                self.render(
                    "market/view.html",
                    user=self.get_current_user(),
                    errors=["Item is not allowed."],
                )
            elif user.has_item(item.name):
                self.render(
                    "market/view.html",
                    user=user,
                    errors=["You have already purchased this item."],
                )
            elif team.money < item.price:
                if options.banking:
                    money = "$%d" % team.money
                else:
                    money = "%d points" % team.money
                message = "You only have %s" % money
                self.render("market/view.html", user=user, errors=[message])
            else:
                logging.info(
                    "%s (%s) purchased '%s' for $%d"
                    % (user.handle, team.name, item.name, item.price)
                )
                self.purchase_item(team, item)
                self.event_manager.item_purchased(user, item)
                self.redirect("/user/market")
        else:
            self.render(
                "market/view.html",
                user=self.get_current_user(),
                errors=["Item does not exist."],
            )

    def purchase_item(self, team, item):
        """Conducts the actual purchase of an item"""
        team.money -= abs(item.price)
        team.items.append(item)
        self.dbsession.add(team)
        self.dbsession.commit()
        self.event_manager.push_score_update()


class MarketDetailsHandler(BaseHandler):

    """Renders views of items in the market"""

    @authenticated
    @use_black_market
    def get(self, *args, **kwargs):
        """Get details on an item"""
        uuid = self.get_argument("uuid", "")
        item = MarketItem.by_uuid(uuid)
        if item is None:
            self.write({"Error": "Item does not exist."})
        elif item.name not in options.allowed_market_items:
            self.write({"Error": "Item is not allowed."})
        else:
            self.write(item.to_dict())
        self.finish()
