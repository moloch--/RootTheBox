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
    limitations under the License
----------------------------------------------------------------------------

This is the main file the defines what URLs get routed to what handlers

"""
# pylint: disable=no-member,unsupported-assignment-operation


import sys
import tornado.locale

from setup import __version__
from os import urandom, _exit, path as os_path
from tornado import netutil, locale
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import options
from sqlalchemy.exc import OperationalError
from alembic.config import Config, command
from builtins import str

from modules.Menu import Menu
from modules.Recaptcha import Recaptcha
from modules.AppTheme import AppTheme
from libs.ConsoleColors import *
from libs.Scoreboard import Scoreboard, score_bots
from libs.GameHistory import GameHistory
from libs.DatabaseConnection import DatabaseConnection
from libs.StringCoding import encode
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
from handlers.FileUploadHandlers import *
from handlers.NotificationHandlers import *
from handlers.MaterialsHandler import *
from handlers.ChefHandler import *
from handlers.StaticFileHandler import StaticFileHandler


try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

# Singletons
io_loop = IOLoop.instance()
game_history = GameHistory.instance()


def get_cookie_secret():
    if options.debug:
        return "Don't use this in production"
    else:
        return encode(urandom(32), "hex")


# Main URL Configuration
# First get base URLs that all game types will require
urls = [
    # Public handlers - PublicHandlers.py
    (r"/login", LoginHandler),
    (r"/oidc", CodeFlowHandler),
    (r"/about", AboutHandler),
    (r"/", HomePageHandler),
    (r"/robots(|\.txt)", FakeRobotsHandler),
    (r"/status", StatusHandler),
    # Scoreboard Handlers - ScoreboardHandlers.py
    (r"/scoreboard", ScoreboardHandler),
    (r"/scoreboard/history", ScoreboardHistoryHandler),
    (r"/scoreboard/feed", ScoreboardFeedHandler),
    (r"/scoreboard/ajax/(.*)", ScoreboardAjaxHandler),
    (r"/scoreboard/wsocket/game_data", ScoreboardDataSocketHandler),
    (r"/scoreboard/wsocket/game_history", ScoreboardHistorySocketHandler),
    (r"/scoreboard/wsocket/pause_score", ScoreboardPauseHandler),
    (r"/teams", TeamsHandler),
    # FileUploadHandlers - FileUploadHandlers.py
    (r"/user/shares/delete", FileDeleteHandler),
    (r"/user/shares/download(.*)", FileDownloadHandler),
    (r"/user/share/files", FileUploadHandler),
    # PasteBin - PastebinHandlers.py
    (r"/user/share/pastebin", PasteHandler),
    (r"/user/share/pastebin/create", CreatePasteHandler),
    (r"/user/share/pastebin/display", DisplayPasteHandler),
    (r"/user/share/pastebin/delete", DeletePasteHandler),
    # Mission handlers - MissionHandlers.py
    (r"/user/missions", MissionsHandler),
    (r"/user/missions/ajax/(.*)", StoryAjaxHandler),
    (r"/user/missions/capture(.*)", FlagCaptureMessageHandler),
    (r"/user/missions/(flag|buyout)", MissionsHandler),
    (r"/user/missions/firstlogin", FirstLoginHandler),
    (r"/user/missions/boxes", BoxHandler),
    (r"/user/missions/hint", PurchaseHintHandler),
    ### BOTNET URLS ###
    # Bot Handlers - BotHandlers.py
    (r"/botnet/connect", BotSocketHandler),
    (r"/botnet/climonitor", BotCliMonitorSocketHandler),
    (r"/botnet/webmonitor", BotWebMonitorSocketHandler),
    (r"/user/bots/download/(windows|linux|monitor)", BotDownloadHandler),
    (r"/user/bots/webmonitor", BotWebMonitorHandler),
    ### BLACK MARKET URLS ###
    # This is only relevant if the black market is enabled
    (r"/scoreboard/wall_of_sheep", ScoreboardWallOfSheepHandler),
    # Market handlers - MarketHandlers.py
    (r"/user/market", MarketViewHandler),
    (r"/user/market/details", MarketDetailsHandler),
    # Upgrade handlers - UpgradeHandlers.py
    (r"/password_security", PasswordSecurityHandler),
    (r"/federal_reserve", FederalReserveHandler),
    (r"/federal_reserve/json/(.*)", FederalReserveAjaxHandler),
    (r"/source_code_market", SourceCodeMarketHandler),
    (r"/source_code_market/download", SourceCodeMarketDownloadHandler),
    (r"/swat", SwatHandler),
    # User handlers - UserHandlers.py
    (r"/user", HomeHandler),
    (r"/user/settings", SettingsHandler),
    (r"/user/settings/(.*)", SettingsHandler),
    (r"/logout", LogoutHandler),
    # Notification handlers - NotificationHandlers.py
    (r"/notifications/all", AllNotificationsHandler),
    (r"/connect/notifications/updates", NotifySocketHandler),
    # Static Handlers - StaticFileHandler.py
    (
        r"/static/(.*\.(jpg|png|gif|css|js|ico|mp3|eot|svg|ttf|woff|otf))",
        StaticFileHandler,
        {"path": "static/"},
    ),
    (
        r"/avatars/(.*\.(png|jpeg|jpg|gif|bmp|svg))",
        StaticFileHandler,
        {"path": "files/avatars/"},
    ),
    (
        r"/story/(.*\.(png|jpeg|jpg|gif|bmp))",
        StaticFileHandler,
        {"path": "files/story/"},
    ),
    (r"/materials/(.*)(?<!/)", StaticFileHandler, {"path": "files/game_materials/"}),
    # Game Materials
    (r"/materials/?", MaterialsHandler),
    (r"/materials/(.*)/", MaterialsHandler),
    (r"/cyberchef/", ChefHandler),
    (r"/cyberchef/(.*)", StaticFileHandler, {"path": "cyberchef/"}),
    # Admin Handlers
    (r"/admin/game", AdminGameHandler),
    (r"/admin/message", AdminMessageHandler),
    (r"/admin/ban/(add|clear|config)", AdminBanHammerHandler),
    (r"/admin/regtoken/(.*)", AdminRegTokenHandler),
    (r"/admin/garbage", AdminGarbageCfgHandler),
    (r"/admin/create/(.*)", AdminCreateHandler),
    (r"/admin/edit/(.*)", AdminEditHandler),
    (r"/admin/view/(.*)", AdminViewHandler),
    (r"/admin/delete/(.*)", AdminDeleteHandler),
    (r"/admin/ajax/objects(.*)", AdminAjaxGameObjectDataHandler),
    (r"/admin/tokentest/(.*)", AdminTestTokenHandler),
    (r"/admin/upgrades/source_code_market(.*)", AdminSourceCodeMarketHandler),
    (r"/admin/upgrades/swat(.*)", AdminSwatHandler),
    (r"/admin/users", AdminManageUsersHandler),
    (r"/admin/users/edit/(user|team)", AdminEditUsersHandler),
    (r"/admin/users/edit/teams/scores", AdminEditTeamsHandler),
    (r"/admin/users/delete/(.*)", AdminDeleteUsersHandler),
    (r"/admin/ajax/(user|team)", AdminAjaxUserHandler),
    (r"/admin/lock/(user|box|flag)", AdminLockHandler),
    (r"/admin/configuration", AdminConfigurationHandler),
    (r"/admin/gitstatus", AdminGitStatusHandler),
    (r"/admin/export/(.*)", AdminExportHandler),
    (r"/admin/import/xml", AdminImportXmlHandler),
    (r"/admin/reset", AdminResetHandler),
    (r"/admin/resetdelete", AdminResetDeleteHandler),
    # Error handlers - ErrorHandlers.py
    (r"/403", UnauthorizedHandler),
    (r"/gamestatus", StopHandler),
    (r"/(.*).php", NoobHandler),
    (r"/admin", NoobHandler),
    (r"/(.*)phpmyadmin(.*)", NoobHandler),
    (r"/administrator(.*)", NoobHandler),
]

# These routes should be disabled if we're not using the database for authentication.
# If database auth is used add them in.
if options.auth == "db":
    urls.insert(2, (r"/reset/token", ResetPasswordHandler))
    urls.insert(2, (r"/reset", ForgotPasswordHandler))
    urls.insert(2, (r"/registration/token", ValidEmailHandler))
    urls.insert(2, (r"/registration", RegistrationHandler))
# For Azure AD authentication we have a simplified Join Team instead of registration.
elif options.auth == "azuread":
    urls.insert(2, (r"/jointeam", JoinTeamHandler))

# This one has to be last
urls.append((r"/(.*)", NotFoundHandler))

app = Application(
    # URL handler mappings
    urls,
    # Randomly generated secret key
    cookie_secret=get_cookie_secret(),
    # Ip addresses that access the admin interface
    admin_ips=options.admin_ips,
    # Template directory
    template_path="templates/",
    # Request that does not pass @authorized will be
    # redirected here
    forbidden_url="/403",
    # Requests that does not pass @authenticated  will be
    # redirected here
    login_url="/login",
    # UI Modules
    ui_modules={"Menu": Menu, "Theme": AppTheme, "Recaptcha": Recaptcha},
    # Enable XSRF protected forms; not optional
    xsrf_cookies=True,
    # Anti-bruteforce
    automatic_ban=options.automatic_ban,
    blacklist_threshold=options.blacklist_threshold,
    blacklisted_ips=[],
    failed_logins={},
    # Debug mode
    debug=options.debug,
    # Flags used to run the game
    game_started=options.autostart_game,
    suspend_registration=options.suspend_registration,
    countdown_timer=False,
    hide_scoreboard=False,
    stop_timer=False,
    temp_global_notifications=None,
    # Callback functions
    score_bots_callback=PeriodicCallback(score_bots, options.bot_reward_interval),
    history_callback=PeriodicCallback(
        game_history.take_snapshot, options.history_snapshot_interval
    ),
    # Scoreboard Highlights
    scoreboard_history={},
    scoreboard_state={},
    # Application version
    version=__version__,
    autoreload=options.autoreload_source,
)


# Update the database schema
def update_db(update=True):
    logging.info("Checking for Database Updates...")
    db_connection = DatabaseConnection(
        database=options.sql_database,
        hostname=options.sql_host,
        port=options.sql_port,
        username=options.sql_user,
        password=options.sql_password,
        dialect=options.sql_dialect,
        ssl_ca=options.sql_sslca,
    )
    alembic_cfg = Config("alembic/alembic.ini")
    alembic_cfg.attributes["configure_logger"] = False
    alembic_cfg.set_main_option("sqlalchemy.url", unquote(str(db_connection)))
    if update:
        command.upgrade(alembic_cfg, "head")
    else:
        command.stamp(alembic_cfg, "head")


def load_history():
    game_history._load()


# Main entry point
def start_server():
    """Main entry point for the application"""
    locale.set_default_locale("en_US")
    locale.load_translations("locale")
    if options.autostart_game:
        app.settings["game_started"] = True
        app.settings["history_callback"].start()
        if options.use_bots:
            app.settings["score_bots_callback"].start()
    # Setup server object
    if options.ssl:
        server = HTTPServer(
            app,
            ssl_options={"certfile": options.certfile, "keyfile": options.keyfile},
            xheaders=options.x_headers,
        )
    else:
        server = HTTPServer(app, xheaders=options.x_headers)
    try:
        sockets = netutil.bind_sockets(options.listen_port, options.listen_interface)
    except (OSError, IOError) as err:
        logging.error("Problem binding socket to port %s", str(options.listen_port))
        if err.errno == 13:
            pypath = sys.executable
            if os_path.islink(pypath):
                pypath = os_path.realpath(pypath)
            logging.error(
                "Possible Fix: sudo setcap CAP_NET_BIND_SERVICE=+eip %s", pypath
            )
        elif err.errno == 98:
            logging.error(
                "The port may be in use by an existing service.  RTB already running?"
            )
        else:
            logging.error(err)
        sys.exit()
    server.add_sockets(sockets)
    if options.debug:
        logging.warning(
            "%sDebug mode is enabled; DO NOT USE THIS IN PRODUCTION%s" % (bold + R, W)
        )
    try:
        logging.info("Building Scoreboard Gamestate...")
        Scoreboard.update_gamestate(app)
    except OperationalError as err:
        if "Table definition has changed" in str(err):
            logging.info("Table definitions have changed -restarting RootTheBox.")
            return "restart"
        else:
            logging.error("There was a problem starting RootTheBox. Error: " + str(err))
    if options.autostart_game:
        logging.info("The game is about to begin, good hunting!")
    try:
        io_loop.start()
    except KeyboardInterrupt:
        sys.stdout.write("\r" + WARN + "Shutdown Everything!\n")
    except:
        logging.exception("Main i/o loop threw exception")
    finally:
        io_loop.stop()
        _exit(0)
