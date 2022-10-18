# -*- coding: utf-8 -*-
"""
Created on Mar 14, 2012

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


from tornado.web import UIModule
from models.User import User
from tornado.options import options


class Menu(UIModule):

    # TODO: Put everything in the session that we need to construct the menu
    #       to avoid having to go to the database to render the menu.

    def render(self, *args, **kwargs):
        """Renders the top menu"""
        if self.handler.session is not None:
            user = User.by_id(self.handler.session["user_id"])
        else:
            user = None
        scoreboard_visible = self.scoreboard_visible(user)
        registration_allowed = self.registration_allowed()
        if self.handler.session is not None:
            if self.handler.session["menu"] == "user":
                return self.render_string(
                    "menu/user.html", user=user, scoreboard_visible=scoreboard_visible
                )
            elif self.handler.session["menu"] == "admin":
                return self.render_string(
                    "menu/admin.html", user=user, scoreboard_visible=scoreboard_visible
                )
        return self.render_string(
            "menu/public.html",
            scoreboard_visible=scoreboard_visible,
            registration_visible=registration_allowed,
        )

    def scoreboard_visible(self, user):
        if options.scoreboard_visibility == "public":
            return True
        if user:
            return options.scoreboard_visibility == "players" or user.is_admin()
        return False

    def registration_allowed(self):
        if options.auth == "azuread":
            return False
        return True
