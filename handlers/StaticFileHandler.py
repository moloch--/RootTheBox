# -*- coding: utf-8 -*-
"""
Created on Mar 13, 2012

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
-------------

Modification of the tornado web StaticFileHandler

"""


import logging

from tornado.web import StaticFileHandler as DefaultStaticHandler
from tornado.options import options


class StaticFileHandler(DefaultStaticHandler):

    """
    Same as the normal Tornado StaticFileHandler with a
    couple overloaded methods.
    """

    session = None
    config = options

    def set_default_headers(self):
        """
        We need to add the security headers here too, especially the
        X-Content-Type-Options header, since we whitelist file extensions.
        this should prevent anyone from serving html/etc from the static
        handler
        """
        if options.force_download_game_materials:
            self.set_header("Content-Disposition", "attachment")
        self.set_header("Server", "Microsoft-IIS/7.5")
        self.add_header("X-AspNetMvc-Version", "3.0")
        self.add_header("X-AspNet-Version", "4.0.30319")
        self.add_header("X-Powered-By", "ASP.NET")
        self.add_header("X-Frame-Options", "DENY")
        self.add_header("X-XSS-Protection", "1; mode=block")
        self.add_header("X-Content-Type-Options", "nosniff")
        if self.config.ssl:
            self.add_header("Strict-Transport-Security", "max-age=31536000;")

    def write_error(self, status_code, **kwargs):
        """Render a generic error page"""
        logging.error(
            "Static file request from %s resulted in %d status"
            % (self.request.remote_ip, status_code)
        )
        # Regardless of error, send a 404
        self.render("public/404.html")
