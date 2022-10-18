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
from tornado.options import options
from models.Theme import Theme


class AppTheme(UIModule):

    theme = Theme.by_name(options.default_theme)

    def render(self, *args, **kwargs):
        """Includes different CSS themes based on user prefs"""

        if (
            options.allow_user_to_change_theme
            and self.handler.session is not None
            and self.handler.session["theme"] is not None
        ):
            return self.render_string(
                "theme/theme.html", theme_files=self.handler.session["theme"]
            )
        else:
            return self.render_string("theme/theme.html", theme_files=self.theme)
