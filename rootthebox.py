#!/usr/bin/env python
'''
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

This file is the main starting point for the application, based on the
command line arguments it calls various components setup/start/etc.

'''

from __future__ import print_function


import os
import nose
import random
import logging

from datetime import datetime
from tornado.options import define, options
from libs.ConsoleColors import *
from libs.ConfigHelpers import save_config
from setup import __version__


current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def start():
    ''' Starts the application '''
    from handlers import start_server
    print(INFO + '%s : Starting application ...' % current_time())
    start_server()


def setup():
    '''
    Creates/bootstraps the database.

    If you're a real developer you'll figure out how to remove the
    warning yourself. Don't merge any code the removes it.
    '''
    is_devel = options.setup.startswith('dev')
    if is_devel:
        print("%sWARNING:%s Setup is in development mode %s" % (
            WARN + bold, W, WARN,
        ))
        message = "I know what the fuck I am doing"
        resp = raw_input(PROMPT + 'Please type "%s": ' % message)
        if resp.replace('"', '').lower().strip() != message.lower():
            os._exit(1)
    print(INFO + '%s : Creating the database ...' % current_time())
    from setup.create_database import create_tables, engine, metadata
    create_tables(engine, metadata, is_devel)
    print(INFO + '%s : Bootstrapping the database ...' % current_time())
    import setup.bootstrap
    # Display Details
    if is_devel:
        environ = bold + R + "Developement boot strap" + W
        details = ", admin password is 'nimda123'."
    else:
        environ = bold + "Production boot strap" + W
        details = '.'
    print(INFO + '%s completed successfully%s' % (environ, details))


def recovery():
    ''' Starts the recovery console '''
    from setup.recovery import RecoveryConsole
    print(INFO + '%s : Starting recovery console ...' % current_time())
    console = RecoveryConsole()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print(INFO + "Have a nice day!")


def setup_xml():
    ''' Imports XML file(s) '''
    from setup.xmlsetup import import_xml
    for index, xml_param in enumerate(xml_params):
        print(INFO + "Processing %d of %d .xml file(s) ..." % (
            index + 1, len(xml_params)
        ))
        import_xml(xml_param)
    print(INFO + "%s : Completed processing of all .xml file(s)" % (
        current_time()
    ))


def tests():
    ''' Creates a temporary sqlite database and runs the unit tests '''
    print(INFO + '%s : Running unit tests ...' % current_time())
    from tests import setup_database, teardown_database
    db_name = 'test-%04s' % random.randint(0, 9999)
    setup_database(db_name)
    nose.run(module='tests', argv=[os.getcwd() + '/tests'])
    teardown_database(db_name)


def restart():
    '''
    Shutdown the actual process and restart the service.
    Useful for rootthebox.cfg changes.
    '''
    pid = os.getpid()
    print(INFO + '%s : Restarting the service (%i)...' % (current_time(), pid))
    os.execl('./setup/restart.sh', '')


def version():
    from sqlalchemy import __version__ as orm_version
    from tornado import version as tornado_version
    print(bold + "Root the Box%s v%s" % (W, __version__))
    print(bold + " SQL Alchemy%s v%s" % (W, orm_version))
    print(bold + "     Torando%s v%s" % (W, tornado_version))


def check_cwd():
    ''' Checks to make sure the cwd is the application root directory '''
    app_root = os.path.dirname(os.path.abspath(__file__))
    if app_root != os.getcwd():
        print(INFO + "Switching CWD to '%s'" % app_root)
        os.chdir(app_root)


########################################################################
#                          Application Settings
########################################################################

# HTTP Server Settings
define("origin",
       default="ws://localhost:8888",
       group="server",
       help="validate websocket connections against this origin")

define("listen_port",
       default=8888,
       group="server",
       help="run instances starting the given port",
       type=int)

define("session_age",
       default=int(60 * 60),
       group="server",
       help="max session age (seconds)",
       type=int)

define("session_regeneration_interval",
       default=int(60 * 60),
       group="server",
       help="regenerate session time frame (seconds)",
       type=int)

define("x_headers",
       default=False,
       group="server",
       help="honor the `X-FORWARDED-FOR` and `X-REAL-IP` http headers",
       type=bool)

define("ssl",
       default=False,
       group="server",
       help="enable the use of ssl/tls",
       type=bool)

define("certfile",
       default="",
       group="server",
       help="the certificate file path (for ssl/tls)")

define("keyfile",
       default="",
       group="server",
       help="the key file path (for ssl/tls)")

define("admin_ips",
       multiple=True,
       default=['127.0.0.1', '::1'],
       group="server",
       help="whitelist of ip addresses that can access the admin ui")

# Application Settings
define("debug",
       default=False,
       group="application",
       help="start the application in debugging mode",
       type=bool)

define("avatar_dir",
       default="./files/avatars",
       group="application",
       help="the directory to store avatar files")

define("share_dir",
       default="./files/shares",
       group="application",
       help="the directory to store shared files")

define("flag_attachment_dir",
       default="./files/flag_attachments",
       group="application",
       help="the directory to store flag attachment files")

define("source_code_market_dir",
       default="./files/source_code_market",
       group="application",
       help="the directory to store souce code market files")

# ReCAPTCHA
define("use_recaptcha",
       default=True,
       help="enable the use of recaptcha for bank passwords",
       group='recaptcha',
       type=bool)

define("recaptcha_api_key",
       default="6LcJJ88SAAAAAFzcmQqDPWGKRQXmJ0DCiZoPWTZf",
       group='recaptcha',
       help="recaptcha api key")

# Database settings
define("sql_dialect",
       default="mysql",
       group="database",
       help="define the type of database (mysql|postgres|sqlite)")

define("sql_database",
       default="rootthebox",
       group="database",
       help="the sql database name")

define("sql_host",
       default="127.0.0.1",
       group="database",
       help="database sever hostname")

define("sql_port",
       default=3306,
       group="database",
       help="database tcp port",
       type=int)

define("sql_user",
       default="rtb",
       group="database",
       help="database username")

define("sql_password",
       default="rtb",
       group="database",
       help="database password, if applicable")

define("log_sql",
       default=False,
       group="database",
       help="Log SQL queries for debugging")

# Memcached settings
define("memcached",
       default="127.0.0.1",
       group="cache",
       help="memcached sever hostname")

define("memcached_port",
       default=11011,
       group="cache",
       help="memcached tcp port",
       type=int)


# Game Settings
define("game_name",
       default="Root the Box",
       group="game",
       help="the name of the current game",
       type=basestring)

define("restrict_registration",
       default=False,
       group="game",
       help="require registration tokens",
       type=bool)

define("public_teams",
       default=True,
       group="game",
       help="allow anyone to create a new team",
       type=bool)

define("max_team_size",
       default=4,
       group="game",
       help="max number of players on any one team",
       type=int)

define("min_user_password_length",
       default=16,
       group="game",
       help="min user password length",
       type=int)

define("max_password_length",
       default=7,
       group="game",
       help="max bank password length",
       type=int)

define("use_bots",
       default=True,
       group="game",
       help="enable the use of botnets",
       type=bool)

define("botnet_db",
       default="./files/botnet.db",
       group="game",
       help="botnet database path")

define("bot_reward",
       default=50,
       group="game",
       help="the reward per-interval for a single bot",
       type=int)

define("use_black_market",
       default=True,
       group="game",
       help="enable the use of the black market",
       type=bool)

define("password_upgrade_cost",
       default=1000,
       group="game",
       help="price to upgrade a password hash algorithm")

define("bribe_cost",
       default=2500,
       group="game",
       help="the base bribe cost to swat another player")

define("whitelist_box_ips",
       default=False,
       group="game",
       help="whitelist box ip addresses (for botnets)",
       type=bool)

define("dynamic_flag_value",
       default=True,
       group="game",
       help="decrease reward for flags based on captures",
       type=bool)

define("flag_value_decrease",
       default=10,
       group="game",
       help="decrease flag reward by this percent per capture",
       type=int)

define("default_theme",
       default="Cyborg",
       group="game",
       help="the default css theme")

define("rank_by",
       default="flags",
       group="game",
       help="rank teams by (flags or money)")

# I/O Loop Settings
define("history_snapshot_interval",
       default=int(60000 * 5),
       group="game",
       help="interval to create history snapshots (milliseconds)",
       type=int)

define("bot_reward_interval",
       default=int(60000 * 15),
       group="game",
       help="interval for rewarding botnets (milliseconds)",
       type=int)

# Process modes
define("setup",
       default="",
       help="setup a database (prod|devel)")

define("xml",
       multiple=True,
       default=[],
       help="import xml file(s)")

define("recovery",
       default=False,
       help="start the recovery console",
       type=bool)

define("start",
       default=False,
       help="start the server",
       type=bool)

define("restart",
       default=False,
       help="restart the server",
       type=bool)

define("version",
       default=False,
       help="display version information and exit",
       type=bool)

define("save",
       default=False,
       help="save the current configuration to file",
       type=bool)

define("config",
       default="files/rootthebox.cfg",
       help="root the box configuration file")


if __name__ == '__main__':

    # We need this to pull the --config option
    options.parse_command_line()

    check_cwd()
    if os.path.isfile(options.config):
        logging.debug("Parsing config file `%s`" % (
            os.path.abspath(options.config),
        ))
        options.parse_config_file(options.config)

    # Make sure that cli args always have president over the file
    options.parse_command_line()
    if options.save:
        save_config()

    if options.setup.lower()[:3] in ['pro', 'dev']:
        setup()
    elif options.start:
        start()
    elif options.restart:
        restart()
    elif options.recovery:
        recovery()
    elif options.version:
        version()
