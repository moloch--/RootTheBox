# -*- coding: utf-8 -*-
"""
    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License
----------------------------------------------------------------------------

Handlers related to configuring the table leds.
"""
# pylint: disable=unused-wildcard-import,no-member

import re

from handlers.BaseHandlers import BaseHandler
from libs.ConfigHelpers import save_config
from libs.LedsManager import (
    clear_last_error,
    get_last_error,
    led_round_start,
    led_stop,
    led_test,
)
from libs.SecurityDecorators import *
from libs.ValidationError import ValidationError
from models.Team import Team
from models.User import ADMIN_PERMISSION

COLOR_REGEX = re.compile(r"^#[0-9a-fA-F]{6}$")

COLOR_OPTIONS = [
    "led_color_flag",
    "led_color_box",
    "led_color_round",
    "led_color_stop",
]


class AdminLedsHandler(BaseHandler):

    """Assign a physical table to each team and configure the led api"""

    def get_int(self, name, default=0):
        try:
            return abs(int(self.get_argument(name, default)))
        except ValueError:
            return default

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render_page()

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        actions = {
            "dismiss": self.dismiss_error,
            "save": self.save,
            "test": self.test_table,
            "test_round": self.test_round,
            "test_stop": self.test_stop,
        }
        action = self.get_argument("action", "save")
        if action not in actions:
            self.render_page(errors=["Unknown action"])
            return
        actions[action]()

    def dismiss_error(self):
        """Clears the led api error banner"""
        clear_last_error()
        self.render_page()

    def save(self):
        """Persists the led settings and the team/table assignments"""
        errors = self.save_settings()
        errors += self.save_tables()
        if len(errors) == 0:
            self.dbsession.commit()
            self.settings_saved = True
            self.render_page(success="Led configuration updated")
        else:
            self.dbsession.rollback()
            self.render_page(errors=errors)

    def save_settings(self):
        """Updates the led options, returns a list of errors"""
        errors = []
        for name in COLOR_OPTIONS:
            value = self.get_argument(name, getattr(self.config, name))
            if COLOR_REGEX.match(value) is None:
                errors.append("%s must be an hex color such as #1fe4f7" % name)
            else:
                setattr(self.config, name, value)
        self.config.led_base_api = self.get_argument(
            "led_base_api", self.config.led_base_api
        )
        self.config.led_round_duration = self.get_int(
            "led_round_duration", self.config.led_round_duration
        )
        self.config.led_stop_duration = self.get_int(
            "led_stop_duration", self.config.led_stop_duration
        )
        return errors

    def save_tables(self):
        """Assigns a table to each team, returns a list of errors"""
        errors = []
        for team in Team.all():
            value = self.get_argument("team_table_%s" % team.uuid, "")
            try:
                team.table_id = value
            except ValidationError as error:
                errors.append(str(error))
                continue
            self.dbsession.add(team)
        return errors

    def test_table(self):
        self.report(led_test(self.get_int("table_id")), "Sent a test to the led api")

    def test_round(self):
        self.report(led_round_start(), "Sent a round start to the led api")

    def test_stop(self):
        self.report(led_stop(), "Sent a stop to the led api")

    def report(self, error, success):
        """Renders the outcome of a led api call"""
        if error is None:
            self.render_page(success=success)
        else:
            self.render_page(errors=[error])

    def render_page(self, errors=None, success=None):
        if errors is not None and not isinstance(errors, list):
            errors = [str(errors)]
        led_error = get_last_error()
        if errors is not None and led_error in errors:
            led_error = None  # Already reported by the form errors
        self.render(
            "admin/leds.html",
            errors=errors,
            success=success,
            led_error=led_error,
            config=self.config,
            teams=Team.all(),
        )

    def on_finish(self):
        """Only a successful save should rewrite the config file"""
        if getattr(self, "settings_saved", False):
            save_config()
