# -*- coding: utf-8 -*-
'''
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
    limitations under the License
----------------------------------------------------------------------------

This is the main file the defines what URLs get routed to what handlers

'''


import sys

from os import urandom, path, _exit
from base64 import b64encode
from modules.Menu import Menu
from modules.Recaptcha import Recaptcha
from modules.CssTheme import CssTheme
from libs.ConsoleColors import *
from libs.Memcache import FileCache
from libs.BotManager import BotManager
from libs.GameHistory import GameHistory
from libs.EventManager import EventManager
from libs.ConfigManager import ConfigManager
from tornado import netutil
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from handlers.BotHandlers import *
from handlers.UserHandlers import *
from handlers.AdminHandlers import *
from handlers.ErrorHandlers import *
from handlers.PublicHandlers import *
from handlers.MarketHandlers import *
from handlers.UpgradeHandlers import *
from handlers.MissionsHandler import *
from handlers.ReporterHandlers import *
from handlers.PastebinHandlers import *
from handlers.ScoreboardHandlers import *
from handlers.ShareUploadHandlers import *
from handlers.NotificationHandlers import *


### Setup and URLs ###
config = ConfigManager.Instance()
if config.cache_files:
    from handlers.StaticFileHandler import StaticFileHandler
else:
    from tornado.web import StaticFileHandler  # lint:ok

app = Application([
                  # Static Handlers - StaticFileHandler.py
                  (r'/static/(.*)',
                      StaticFileHandler, {'path': 'static'}),
                  (r'/avatars/(.*)',
                      StaticFileHandler, {'path': 'files/avatars'}),

                  # Bot Handlers - BotHandlers.py
                  (r'/botnet/connect', BotHandler),

                  # ShareUploadHandlers - ShareUploadHandlers.py
                  (r'/user/shares/download(.*)', ShareDownloadHandler),
                  (r'/user/share/files', ShareUploadHandler),

                  # PasteBin - PastebinHandlers.py
                  (r'/user/share/pastebin', PasteHandler),
                  (r'/user/share/pastebin/create', CreatePasteHandler),
                  (r'/user/share/pastebin/display', DisplayPasteHandler),
                  (r'/user/share/pastebin/delete', DeletePasteHandler),

                  # Market handlers - MarketHandlers.py
                  (r'/user/market', MarketViewHandler),
                  (r'/user/market/details', MarketDetailsHandler),

                  # Upgrade handlers - UpgradeHandlers.py
                  (r'/password_security', PasswordSecurityHandler),
                  (r'/federal_reserve', FederalReserveHandler),
                  (r'/federal_reserve/json/(.*)', FederalReserveAjaxHandler),
                  (r'/source_code_market', SourceCodeMarketHandler),
                  (r'/source_code_market/download', SourceCodeMarketDownloadHandler),
                  (r'/swat', SwatHandler),

                  # Mission handlers - MissionHandlers.py
                  (r'/user/missions', MissionsHandler),
                  (r'/user/missions/(.*)', MissionsHandler),

                  # User handlers - UserHandlers.py
                  (r'/user', HomeHandler),
                  (r'/user/settings(.*)', SettingsHandler),

                  # Admin Handlers - AdminHandlers.py
                  (r'/admin/regtoken/(.*)', AdminRegTokenHandler),
                  (r'/admin/create/(.*)', AdminCreateHandler),
                  (r'/admin/edit/(.*)', AdminEditHandler),
                  (r'/admin/view/(.*)', AdminViewHandler),
                  (r'/admin/delete/(.*)', AdminDeleteHandler),
                  (r'/admin/ajax/objects(.*)', AdminAjaxObjectDataHandler),
                  (r'/admin/upgrades/source_code_market(.*)', AdminSourceCodeMarketHandler),
                  (r'/admin/upgrades/swat(.*)', AdminSwatHandler),
                  (r'/admin/lock', AdminLockHandler),

                  # Notificaiton handlers - NotificationHandlers.py
                  (r'/notifications/all', AllNotificationsHandler),
                  (r'/notifications/wsocket/updates', NotifySocketHandler),

                  # Scoreboard Handlers - ScoreboardHandlers.py
                  (r'/scoreboard', ScoreboardHandler),
                  (r'/scoreboard/history/(.*)', ScoreboardHistoryHandler),
                  (r'/scoreboard/ajax/(.*)', ScoreboardAjaxHandler),
                  (r'/scoreboard/wsocket/game_data', ScoreboardDataSocketHandler),
                  (r'/scoreboard/wsocket/game_history', ScoreboardHistorySocketHandler),
                  (r'/scoreboard/wall_of_sheep', ScoreboardWallOfSheepHandler),

                  # Public handlers - PublicHandlers.py
                  (r'/login', LoginHandler),
                  (r'/registration', RegistrationHandler),
                  (r'/about', AboutHandler),
                  (r'/logout', LogoutHandler),
                  (r'/', HomePageHandler),

                  # Error handlers - ErrorHandlers.py
                  (r'/403', UnauthorizedHandler),
                  (r'/(.*).php', NoobHandler),
                  (r'/admin', NoobHandler),
                  (r'/(.*)phpmyadmin(.*)', NoobHandler),
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
                  ui_modules={
                      "Menu": Menu,
                      "CssTheme": CssTheme,
                      "Recaptcha": Recaptcha,
                  },

                  # Enable XSRF protected forms; not optional
                  xsrf_cookies=True,

                  # Recaptcha Settings
                  recaptcha_enable=config.recaptcha_enable,
                  recaptcha_private_key=config.recaptcha_private_key,

                  # WebSocket Host IP Address
                  domain=config.domain,
                  port=config.listen_port,

                  # Special file directories
                  avatar_dir=path.abspath('files/avatars/'),
                  shares_dir=path.abspath('files/shares/'),
                  source_code_market_dir=path.abspath('files/source_code_market'),

                  # Event manager
                  event_manager=EventManager.Instance(),

                  # Debug mode
                  debug=config.debug,

                  # Application version
                  version='0.3.0'
                  )


# Main entry point
def start_server():
    ''' Main entry point for the application '''
    sockets = netutil.bind_sockets(config.listen_port)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    io_loop = IOLoop.instance()
    bot_manager = BotManager.Instance()
    scoring = PeriodicCallback(
        bot_manager.scoring, 5 * 60000, io_loop=io_loop
    )
    scoring.start()
    try:
        sys.stdout.write("\r" + INFO + "The game has begun, good hunting!\n")
        if config.debug:
            sys.stdout.write(WARN + "WARNING: Debug mode is enabled.\n")
        sys.stdout.flush()
        game_history = GameHistory.Instance()
        history_callback = PeriodicCallback(
            game_history.take_snapshot, 60000, io_loop=io_loop
        )
        history_callback.start()
        io_loop.start()
    except KeyboardInterrupt:
        print('\r' + WARN + 'Shutdown Everything!')
    except:
      logging.exception("Main i/o loop threw exception")
    finally:
        io_loop.stop()
        if config.debug and raw_input(PROMPT + "Flush Memcache? [Y/n]: ").lower() == 'y':
            print(INFO + 'Flushing cache ...'),
            FileCache.flush()
            print('OK')
        _exit(0)
