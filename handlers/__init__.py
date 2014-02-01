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
from modules.Menu import Menu
from modules.Recaptcha import Recaptcha
from modules.CssTheme import CssTheme
from libs.ConsoleColors import *
from libs.Memcache import FileCache
from libs.Scoreboard import score_bots
from libs.BotManager import BotManager, ping_bots
from libs.GameHistory import GameHistory
from libs.EventManager import EventManager
from libs.ConfigManager import ConfigManager
from tornado import netutil
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from handlers.BotnetHandlers import *
from handlers.UserHandlers import *
from handlers.AdminHandlers import *
from handlers.ErrorHandlers import *
from handlers.PublicHandlers import *
from handlers.MarketHandlers import *
from handlers.UpgradeHandlers import *
from handlers.MissionsHandler import *
from handlers.PastebinHandlers import *
from handlers.ScoreboardHandlers import *
from handlers.ShareUploadHandlers import *
from handlers.NotificationHandlers import *


### Setup cache
config = ConfigManager.Instance()
if config.cache_files:
    from handlers.StaticFileHandler import CachedStaticFileHandler as StaticFileHandler
else:
    from handlers.StaticFileHandler import StaticFileHandler as StaticFileHandler


### Main URL Configuration

# First get base URLs that all game types will require
urls = [
    # Static Handlers - StaticFileHandler.py
    (r'/static/(.*\.(jpg|png|css|js|ico|swf|flv|eot|svg|ttf|woff|otf))',
        StaticFileHandler, {'path': 'static/'}),
    (r'/avatars/(.*\.(png|jpeg|jpg|gif|bmp))',
        StaticFileHandler, {'path': 'files/avatars/'}),

    # ShareUploadHandlers - ShareUploadHandlers.py
    (r'/user/shares/download(.*)', ShareDownloadHandler),
    (r'/user/share/files', ShareUploadHandler),

    # PasteBin - PastebinHandlers.py
    (r'/user/share/pastebin', PasteHandler),
    (r'/user/share/pastebin/create', CreatePasteHandler),
    (r'/user/share/pastebin/display', DisplayPasteHandler),
    (r'/user/share/pastebin/delete', DeletePasteHandler),

    # Mission handlers - MissionHandlers.py
    (r'/user/missions', MissionsHandler),
    (r'/user/missions/capture',FlagSubmissionHandler),
    (r'/user/missions/(flag|buyout)', MissionsHandler),
    (r'/user/missions/firstlogin', FirstLoginHandler),
    (r'/user/missions/boxes', BoxHandler),
    (r'/user/missions/hint', PurchaseHintHandler),

    # User handlers - UserHandlers.py
    (r'/user', HomeHandler),
    (r'/user/settings', SettingsHandler),
    (r'/user/settings/(.*)', SettingsHandler),
    (r'/logout', LogoutHandler),

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
    (r'/admin/configuration', AdminConfigurationHandler),
    (r'/admin/export/(.*)', AdminExportHandler),
    (r'/admin/import/xml', AdminImportXmlHandler),
    (r'/admin/logviewer', AdminLogViewerHandler),
    (r'/admin/logviewer/wsocket', AdminLogViewerSocketHandler),
    (r'/admin/garbage', AdminGarbageCfgHandler),

    # Notificaiton handlers - NotificationHandlers.py
    (r'/notifications/all', AllNotificationsHandler),
    (r'/notifications/wsocket/updates', NotifySocketHandler),

    # Scoreboard Handlers - ScoreboardHandlers.py
    (r'/scoreboard', ScoreboardHandler),
    (r'/scoreboard/history/(.*)', ScoreboardHistoryHandler),
    (r'/scoreboard/ajax/(.*)', ScoreboardAjaxHandler),
    (r'/scoreboard/wsocket/game_data', ScoreboardDataSocketHandler),
    (r'/scoreboard/wsocket/game_history', ScoreboardHistorySocketHandler),
    (r'/teams', TeamsHandler),

    # Public handlers - PublicHandlers.py
    (r'/login', LoginHandler),
    (r'/registration', RegistrationHandler),
    (r'/about', AboutHandler),
    (r'/', HomePageHandler),
    (r'/robots(|\.txt)', FakeRobotsHandler),

    # Error handlers - ErrorHandlers.py
    (r'/403', UnauthorizedHandler),
    (r'/(.*).php', NoobHandler),
    (r'/admin', NoobHandler),
    (r'/(.*)phpmyadmin(.*)', NoobHandler),
    (r'/administrator(.*)', NoobHandler)
]

# If the game is configured to use bots, associate the handlers necessary
if config.use_bots:
    urls += [
        # Bot Handlers - BotHandlers.py
        (r'/botnet/connect', BotSocketHandler),
        (r'/botnet/climonitor', BotCliMonitorSocketHandler),
        (r'/botnet/webmonitor', BotWebMonitorSocketHandler),
        (r'/user/bots/download/(windows|linux|monitor)', BotDownloadHandler),
        (r'/user/bots/webmonitor', BotWebMonitorHandler)
    ]

# If the game is configured to use the black market, associate the handlers necessary
if config.use_black_market:
    urls += [
        # This is only relevent if the black market is enabled
        (r'/scoreboard/wall_of_sheep', ScoreboardWallOfSheepHandler),

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
    ]

# This one has to be last
urls.append((r'/(.*)', NotFoundHandler))

app = Application(
    # URL handler mappings
    urls,

    # Randomly generated secret key
    cookie_secret=urandom(32).encode('base64'),

    # Ip addresses that access the admin interface
    admin_ips=config.admin_ips,

    # Template directory
    template_path='templates/',

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

    # Current domain setting
    domain=config.domain,

    # WebSocket connection URL
    ws_connect=config.ws_connect,

    port=config.listen_port,

    # Special file directories
    avatar_dir=path.abspath('files/avatars/'),
    shares_dir=path.abspath('files/shares/'),
    source_code_market_dir=path.abspath('files/source_code_market/'),

    # Event manager
    event_manager=EventManager.Instance(),

    # Debug mode
    debug=config.debug,

    # Application version
    game_name=config.game_name,
    version='0.3.0',
)


# Main entry point
def start_server():
    ''' Main entry point for the application '''
    if config.debug:
        sys.stdout.write(WARN+"WARNING: Debug mode is enabled in "+config.filename)
        sys.stdout.flush()
        logging.warn("Debug mode is enabled; some security measures will be ignored")

    # Setup server object
    if config.use_ssl:
        server = HTTPServer(app,
            ssl_options={
                "certfile": config.certfile,
                "keyfile": config.keyfile,
            },
            xheaders=config.x_headers
        )
    else:
        server = HTTPServer(app, xheaders=config.x_headers)

    # Bind to a socket
    sockets = netutil.bind_sockets(config.listen_port)
    server.add_sockets(sockets)

    # Start the i/o loop, and callbacks
    try:
        io_loop = IOLoop.instance()
        game_history = GameHistory.Instance()
        history_callback = PeriodicCallback(
            game_history.take_snapshot,
            config.history_snapshot_interval,
            io_loop=io_loop
        )
        if config.use_bots:
            scoring_callback = PeriodicCallback(
                score_bots,
                config.bot_reward_interval,
                io_loop=io_loop
            )
            bot_ping_callback = PeriodicCallback(
                ping_bots, 30000, io_loop=io_loop
            )
            bot_ping_callback.start()
            scoring_callback.start()
        history_callback.start()
        io_loop.start()
    except KeyboardInterrupt:
        sys.stdout.write('\r'+WARN+'Shutdown Everything!\n')
    except:
        logging.exception("Main i/o loop threw exception")
    finally:
        io_loop.stop()
        if config.debug and raw_input(PROMPT+"Flush Memcache? [Y/n]: ").lower() == 'y':
            sys.stdout.write(INFO+'Flushing cache ... '),
            FileCache.flush()
            sys.stdout.write('okay\n')
        _exit(0)
