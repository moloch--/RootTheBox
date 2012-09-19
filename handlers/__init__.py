# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch

    Copyright [2012] [Redacted Labs]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


import sys
import models
import logging

from time import sleep
from os import urandom, path
from base64 import b64encode
from modules.Menu import Menu
from modules.Sidebar import Sidebar
from modules.CssTheme import CssTheme
from libs.ConsoleColors import *
from libs.Memcache import FileCache
from libs.Session import SessionManager
from libs.HostNetworkConfig import HostNetworkConfig
from libs.AuthenticateReporter import scoring_round
from libs.ConfigManager import ConfigManager
from tornado import netutil, options
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from handlers.UserHandlers import *
from handlers.AdminHandlers import *
from handlers.ErrorHandlers import *
from handlers.PublicHandlers import *
from handlers.HashesHandlers import *
from handlers.ReporterHandlers import *
from handlers.PastebinHandlers import *
from handlers.WebsocketHandlers import *
from handlers.ScoreboardHandlers import *

from handlers.StaticFileHandler import StaticFileHandler

config = ConfigManager.Instance()
app = Application([
                  # Static Handlers - Serves static CSS, JavaScript and
                  # image files
                  (r'/static/(.*)',
                   StaticFileHandler, {'path': 'static'}),
                  (r'/avatars/(.*)',
                   StaticFileHandler, {'path': 'files/avatars'}),

                  # Reporter Handlers - Communication with reporters
                  (r'/reporter/register', ReporterRegistrationHandler),

                  # User Handlers - Serves user related pages
                  # File share Handlers
                  (r'/user/shares/download(.*)', ShareDownloadHandler),
                  (r'/user/share/files',
                   ShareUploadHandler),
                  
                  # Text share Handlers
                  (r'/user/share/text', PastebinHandler),
                  (r'/pastebin/view(.*)', DisplayPostHandler),
                  (r'/pastebin/delete(.*)', DeletePostHandler),
                  
                  # User handlers
                  (r'/user/settings(.*)', SettingsHandler),
                  (r'/user/team/ajax(.*)', TeamAjaxHandler),
                  (r'/user/team', TeamViewHandler),
                  (r'/user/reporter', ReporterHandler),
                  (r'/user', HomeHandler),

                  # Hashes Handlers - Serves hash related pages
                  (r'/hashes', HashesHandler),
                  (r'/hashes/ajax(.*)', HashesAjaxHandler),
                  (r'/wallofsheep', WallOfSheepHandler),

                  # Scoreboard Handlers - Severs scoreboard related
                  # pages
                  (r'/scoreboard', ScoreBoardHandler),
                  (r'/all_time(.*)', AllTimeHandler),
                  (r'/pie_chart(.*)', PieChartHandler),
                  (r'/bar_chart(.*)', BarChartHandler),

                  # Admin Handlers - Administration pages
                  (r'/admin/create/(.*)', AdminCreateHandler),
                  (r'/admin/view/(.*)', AdminViewHandler),

                  # WebSocket Handlers - Websocket communication
                  # handlers
                  (r'/websocket', WebsocketHandler),

                  # Public handlers - Serves all public pages
                  (r'/login', LoginHandler),
                  (r'/registration', UserRegistraionHandler),
                  (r'/about', AboutHandler),
                  (r'/logout', LogoutHandler),
                  (r'/', HomePageHandler),

                  # Error handlers - Serves error pages
                  (r'/403', UnauthorizedHandler),
                  (r'/(.*).php(.*)', NoobHandler),
                  (r'/admin', NoobHandler),
                  (r'/administrator', NoobHandler),
                  (r'/(.*)', NotFoundHandler)
                  ],

                  # Randomly generated secret key
                  cookie_secret=b64encode(urandom(64)),

                  # Ip addresses that access the admin interface
                  admin_ips=config.admin_ips,

                  # Template directory
                  template_path='templates',

                  # Request that does not pass @authorized will be
                  # redirected here
                  forbidden_url='/403',

                  # Requests that does not pass @authenticated  will be
                  # redirected here
                  login_url='/login',

                  # UI Modules
                  ui_modules={"Menu": Menu, "CssTheme": CssTheme, "Sidebar": Sidebar},

                  # Enable XSRF forms
                  xsrf_cookies=True,

                  # Recaptcha Settings
                  recaptcha_enable=config.recaptcha_enable,
                  recaptcha_private_key=config.recaptcha_private_key,

                  # WebSocket Host IP Address
                  ws_ip_address=config.domain,
                  ws_port=config.listen_port,

                  # Special file directories
                  avatar_dir=path.abspath('files/avatars/'),
                  shares_dir=path.abspath('files/shares/'),

                  # Milli-Seconds between scoring
                  ticks=int(60 * 1000),

                  # Milli-Seconds between session clean up
                  clean_up_timeout=int(60 * 1000),

                  # Debug mode
                  debug=config.debug,

                  # Application version
                  version='0.3'
                  )

# Main entry point


def start_game():
    ''' Main entry point for the application '''
    sockets = netutil.bind_sockets(config.listen_port)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    io_loop = IOLoop.instance()
    session_manager = SessionManager.Instance()
    scoring = PeriodicCallback(
        scoring_round, app.settings['ticks'], io_loop=io_loop)
    session_clean_up = PeriodicCallback(session_manager.clean_up,
                                        app.settings['clean_up_timeout'], io_loop=io_loop)
    scoring.start()
    session_clean_up.start()
    try:
        for count in range(3, 0, -1):
            sys.stdout.write(
                "\r" + INFO + "The game will begin in ... %d" % (count,))
            sys.stdout.flush()
            sleep(1)
        sys.stdout.write("\r" + INFO + "The game has begun, good hunting!\n")
        sys.stdout.flush()
        io_loop.start()
    except KeyboardInterrupt:
        print('\r' + WARN + 'Shutdown Everything!')
        FileCache.flush()
        session_clean_up.stop()
        io_loop.stop()
