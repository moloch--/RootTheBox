# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

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
'''


import os
import sys
import urllib
import socket
import getpass
import logging
import ConfigParser

from libs.ConsoleColors import *
from libs.Singleton import Singleton
from sqlalchemy import create_engine
from libs.LoggingHelpers import ObservableLoggingHandler


# .basicConfig must be called prior to ANY call to logging.XXXX so make sure
# this module gets imported prior to any logging!
logging.basicConfig(format='\r[%(levelname)s] %(asctime)s - %(message)s', level=logging.NOTSET)
logging_levels = {
       'notset': logging.NOTSET,
        'debug': logging.DEBUG,
         'info': logging.INFO,
  'information': logging.INFO,
         'warn': logging.WARN,
      'warning': logging.WARN,
}


@Singleton
class ConfigManager(object):
    ''' Central class which handles any user-controlled settings '''

    # Under the hood attributes
    _domain_warned = False
    _db_connection = None

    # Game Setup
    _game_name = None
    _restrict_registration = None
    _public_teams = None
    _max_team_size = None
    _max_password_length = None

    # Feature enable/disable
    _use_bots = None
    _bot_reward = None
    _use_black_market = None
    _password_upgrade_cost = None
    _bribe_cost = None
    _whitelist_box_ips = None
    _dynamic_flag_value = None
    _flag_value_decrease = None

    def __init__(self, cfg_file='rootthebox.cfg'):
        self.filename = cfg_file
        if os.path.exists(cfg_file) and os.path.isfile(cfg_file):
            self.conf_path = os.path.abspath(cfg_file)
        else:
            sys.stderr.write(WARN + "No configuration file found at: %s." % self.conf_path)
            os._exit(1)
        self.refresh()
        self._logging()

    def _logging(self):
        ''' Load network configurations '''
        level = self.config.get("Logging", 'console_level').lower()
        logger = logging.getLogger()
        logger.setLevel(logging_levels.get(level, logging.NOTSET))
        if self.config.getboolean("Logging", 'file_logs'):
            self._file_logger(logger)
        if self.enable_logviewer:
            self._websocket_logger(logger)

    def _file_logger(self, logger):
        ''' Configure File Logger '''
        file_log = logging.FileHandler('%s' % self.logfile)
        logger.addHandler(file_log)
        file_format = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
        file_log.setFormatter(file_format)
        flevel = self.config.get("Logging", 'file_level').lower()
        file_log.setLevel(logging_levels.get(flevel, logging.NOTSET))

    def _websocket_logger(self, logger):
        ''' Configure WebSocket Logger '''
        ws_log = ObservableLoggingHandler.instance()
        logger.addHandler(ws_log)
        msg_format = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
        ws_log.setFormatter(msg_format)
        ws_log.setLevel(logging.DEBUG)

    def refresh(self):
        ''' Refresh config file settings '''
        self.config = ConfigParser.SafeConfigParser()
        with open(self.conf_path, 'r') as fp:
            self.config.readfp(fp)

    def save(self):
        ''' Write current config to file '''
        # Set game config
        self.config.set("Game", "game_name", self.game_name)
        self.config.set("Game", "public_teams", str(self.public_teams))
        self.config.set("Game", "max_team_size", str(self.max_team_size))
        self.config.set("Game", "max_password_length", str(self.max_password_length))
        self.config.set("Game", "restrict_registration", str(self.restrict_registration))
        self.config.set("Game", "use_black_market", str(self.use_black_market))
        self.config.set("Game", "use_bots", str(self.use_bots))
        self.config.set("Game", "bot_reward", str(self.bot_reward))
        self.config.set("Game", "password_upgrade_cost", str(self.password_upgrade_cost))
        self.config.set("Game", "bribe_cost", str(self.bribe_cost))
        self.config.set("Game", "whitelist_box_ips", str(self.whitelist_box_ips))
        with open(self.conf_path, 'w') as fp:
            self.config.write(fp)

    #####################################################################
    #######################  [ SERVER SETTINGS ]  #######################
    #####################################################################

    @property
    def memcached(self):
        ''' Memached settings, cannot be changed from webui '''
        memcached_host = self.config.get("Cache", 'memcached_host')
        memcached_port = self.config.getint("Cache", 'memcached_port')
        return "%s:%d" % (memcached_host, memcached_port)

    @property
    def session_age(self):
        ''' Max session age in seconds '''
        return abs(self.config.getint("Cache", 'session_age'))

    @property
    def session_regeneration_interval(self):
        return abs(self.config.getint("Cache", 'session_regeneration_interval'))

    @property
    def admin_ips(self):
        ''' Whitelist admin ip address, this may be bypassed if x-headers is enabled '''
        ips = self.config.get("Security", 'admin_ips')
        ips = ips.replace(" ", "").split(',')
        ips.append('127.0.0.1')
        ips.append('::1')
        return tuple(set(ips))

    @property
    def x_headers(self):
        ''' Enable/disable HTTP X-Headers '''
        xheaders = self.config.getboolean("Security", 'x-headers')
        if xheaders:
            logging.warn("X-Headers is enabled, this may affect IP security restrictions")
        return xheaders

    @property
    def recaptcha_enabled(self):
        ''' Enable/Disable use of recaptcha '''
        return self.config.getboolean("Recaptcha", 'use_recaptcha')

    @recaptcha_enabled.setter
    def recaptcha_enabled(self, value):
        assert isinstance(value, bool)
        self.config.set("Recaptcha", 'use_recaptcha', str(value))

    @property
    def recaptcha_private_key(self):
        ''' Recaptcha API key '''
        return self.config.get("Recaptcha", 'private_key')

    @property
    def listen_port(self):
        ''' Web app listen port, only read once '''
        lport = self.config.getint("Server", 'port')
        if not 0 < lport < 65535:
            logging.fatal("Listen port not in valid range: %d" % lport)
            os._exit(1)
        return lport

    @property
    def logfile(self):
        return self.config.get("Logging", 'logfile')

    @property
    def enable_logviewer(self):
        return self.config.getboolean("Logging", 'enable_logviewer')

    @property
    def debug(self):
        ''' Debug mode '''
        return self.config.getboolean("Server", 'debug')

    @property
    def domain(self):
        ''' Automatically resolve domain, or use manual setting '''
        _domain = self.config.get("Server", 'domain').strip()
        if _domain.lower() == 'auto':
            try:
                _domain = socket.gethostbyname(socket.gethostname())
                # On some Linux systems the hostname resolves to ~127.0.0.1
                # per /etc/hosts, so fallback and try to get the fqdn if we can.
                if _domain.startswith('127.'):
                    _domain = socket.gethostbyname(socket.getfqdn())
            except:
                logging.warn("Failed to automatically resolve domain, please set manually")
                _domain = 'localhost'
            logging.debug("Domain was automatically configured to '%s'" % _domain)
        if _domain == 'localhost' or _domain.startswith('127.') or _domain == '::1':
            if not self._domain_warned:
                self._domain_warned = True
                logging.warn("Possible misconfiguration 'domain' is set to 'localhost'")
        return _domain

    @property
    def origin(self):
        ''' Origin URL (e.g. http://192.168.1.1:8888) '''
        default = True if (self.use_ssl and self.listen_port == 443) \
                        or not self.use_ssl and self.listen_port == 80 \
                        else False
        http = 'https://' if self.use_ssl else 'http://'
        if default:
            return "%s%s" % (http, self.domain)
        else:
            return "%s%s:%d" % (http, self.domain, self.listen_port)

    @property
    def ws_connect(self):
        ''' Websocket connection URL '''
        default = True if (self.use_ssl and self.listen_port == 443) \
                        or not self.use_ssl and self.listen_port == 80 \
                        else False
        ws = 'wss://' if self.use_ssl else 'ws://'
        if default:
            return '%s%s' % (ws, self.domain)
        else:
            return '%s%s:%s' % (ws, self.domain, self.listen_port)

    @property
    def bootstrap(self):
        return self.config.get("Server", 'bootstrap')

    @property
    def default_theme(self):
        return self.config.get("Server", "theme")

    @property
    def use_ssl(self):
        ''' Enable/disabled SSL server '''
        return self.config.getboolean("Ssl", 'use_ssl')

    @property
    def certfile(self):
        ''' SSL Certificate file path '''
        cert = os.path.abspath(self.config.get("Ssl", 'certificate_file'))
        if not os.path.exists(cert):
            logging.fatal("SSL misconfiguration, certificate file '%s' not found." % cert)
            os._exit(1)
        return cert

    @property
    def keyfile(self):
        ''' SSL Key file path '''
        key = os.path.abspath(self.config.get("Ssl", 'key_file'))
        if not os.path.exists(key):
            logging.fatal("SSL misconfiguration, key file '%s' not found." % key)
            os._exit(1)
        return key

    #####################################################################
    ########################  [ GAME SETTINGS ]  ########################
    #####################################################################

    @property
    def game_name(self):
        if self._game_name is None:
            self._game_name = self.config.get("Game", 'game_name')[:20]
        return self._game_name

    @game_name.setter
    def game_name(self, value):
        if value != self._game_name:
            self._game_name = value[:20]

    @property
    def restrict_registration(self):
        ''' Enable/disable registration tokens '''
        if self._restrict_registration is None:
            self._restrict_registration = self.config.getboolean("Game", 'restrict_registration')
        return self._restrict_registration

    @restrict_registration.setter
    def restrict_registration(self, value):
        self._restrict_registration = bool(value)

    @property
    def public_teams(self):
        ''' Allow new users to create their own teams '''
        if self._public_teams is None:
            self._public_teams = self.config.getboolean("Game", 'public_teams')
        return self._public_teams

    @public_teams.setter
    def public_teams(self, value):
        self._public_teams = bool(value)

    @property
    def max_team_size(self):
        if self._max_team_size is None:
            self._max_team_size = self.config.getint("Game", 'max_team_size')
        return self._max_team_size

    @max_team_size.setter
    def max_team_size(self, value):
        if isinstance(value, basestring) and not value.strip().isdigit():
            ValueError("Max team size must be a number")
        if int(value) <= 0:
            raise ValueError("Max team size must be at least 1")
        self._max_team_size = int(value)

    @property
    def max_password_length(self):
        if self._max_password_length is None:
            self._max_password_length = abs(self.config.getint("Game", 'max_password_length'))
        return self._max_password_length

    @max_password_length.setter
    def max_password_length(self, value):
        if isinstance(value, basestring) and not value.strip().isdigit():
            ValueError("Max password length must be a number")
        if int(value) <= 0:
            raise ValueError("Max password length must be at least 1")
        self._max_password_length = int(value)

    @property
    def use_bots(self):
        ''' Whether bots should be enabled in this game '''
        if self._use_bots is None:
            self._use_bots = self.config.getboolean("Game", "use_bots")
        return self._use_bots

    @use_bots.setter
    def use_bots(self, value):
        self._use_bots = bool(value)

    @property
    def bot_reward(self):
        ''' Reward per bot per interval '''
        if self._bot_reward is None:
            self._bot_reward = abs(self.config.getint("Game", 'bot_reward'))
        return self._bot_reward

    @bot_reward.setter
    def bot_reward(self, value):
        if isinstance(value, basestring) and not value.strip().isdigit():
            ValueError("Bot reward must be a number")
        if int(value) <= 0:
            raise ValueError("Bot reward must be at least 1")
        self._bot_reward = int(value)

    @property
    def use_black_market(self):
        ''' Whether the black market should be enabled in this game '''
        if self._use_black_market is None:
            self._use_black_market = self.config.getboolean("Game", "use_black_market")
        return self._use_black_market

    @use_black_market.setter
    def use_black_market(self, value):
        self._use_black_market = bool(value)

    @property
    def password_upgrade_cost(self):
        if self._password_upgrade_cost is None:
            self._password_upgrade_cost = abs(self.config.getint("Game", 'password_upgrade_cost'))
        return self._password_upgrade_cost

    @password_upgrade_cost.setter
    def password_upgrade_cost(self, value):
        if isinstance(value, basestring) and not value.strip().isdigit():
            ValueError("Password upgrade cost must be a number")
        if int(value) <= 0:
            raise ValueError("Password upgrade cost must be at least 1")
        self._password_upgrade_cost = int(value)

    @property
    def bribe_cost(self):
        ''' Base amount of a SWAT bribe '''
        if self._bribe_cost is None:
            self._bribe_cost = abs(self.config.getint("Game", 'bribe_cost'))
        return self._bribe_cost

    @bribe_cost.setter
    def bribe_cost(self, value):
        if isinstance(value, basestring) and not value.strip().isdigit():
            ValueError("Bribe price must be a number")
        if int(value) <= 0:
            raise ValueError("Bribe price must be at least 1")
        self._bribe_cost = int(value)

    @property
    def whitelist_box_ips(self):
        if self._whitelist_box_ips is None:
            self._whitelist_box_ips = self.config.getboolean('Game', 'whitelist_box_ips')
        return self._whitelist_box_ips

    @whitelist_box_ips.setter
    def whitelist_box_ips(self, value):
        self._whitelist_box_ips = bool(value)

    @property
    def dynamic_flag_value(self):
        if self._dynamic_flag_value is None:
            self._dynamic_flag_value = self.config.getboolean('Game', 'dynamic_flag_value')
        return self._dynamic_flag_value

    @property.setter
    def dynamic_flag_value(self, value):
        self._dynamic_flag_value = bool(value)

    @property
    def flag_value_decrease(self):
        if self._flag_value_decrease is None:
            self._flag_value_decrease = self.config.getboolean('Game', 'flag_value_decrease')
        return self._flag_value_decrease

    @property.setter
    def flag_value_decrease(self, value):
        self._flag_value_decrease = int(value)

    #####################################################################
    #######################  [ I/O LOOP SETTINGS ] ######################
    #####################################################################

    @property
    def history_snapshot_interval(self):
        conf = self.config.getint("Game", 'history_snapshot_interval')
        return 60000 * conf

    @property
    def bot_reward_interval(self):
        ''' Check bots every so many minutes '''
        _interval = self.config.getint("Game", 'bot_reward_interval')
        return  60000 * _interval

    #####################################################################
    ######################  [ DIRECTORY SETTINGS ]  #####################
    #####################################################################

    @property
    def avatar_dir(self):
        return os.path.abspath('files/avatars') + '/'

    @property
    def file_uploads_dir(self):
        return os.path.abspath('files/shares/') + '/'

    #####################################################################
    ######################  [ DATABASE SETTINGS ]  ######################
    #####################################################################

    @property
    def log_sql(self):
        ''' This value is only read once, no setter '''
        return self.config.getboolean("Database", 'orm_sql')

    @property
    def bot_sql(self):
        ''' This value is only read once, no setter '''
        return self.config.getboolean("Database", 'bot_sql')

    @property
    def db_connection(self):
        ''' Db connection string, only read once '''
        if self._db_connection is None:
            db = self.config.get("Database", 'dialect').lower().strip()
            if db == 'sqlite':
                db_conn = self.__sqlite__()
            elif db == 'postgresql':
                db_conn = self.__postgresql__()
            elif db == 'mysql':
                db_conn = self.__mysql__()
            self._test_db_connection(db_conn)
            self._db_connection = db_conn
        return self._db_connection

    @db_connection.setter
    def db_connection(self, value):
        self._test_db_connection(value)
        self._db_connection = value

    def __postgresql__(self):
        '''
        Configure to use postgresql, there is not built-in support for postgresql
        so make sure we can import the 3rd party python lib 'pypostgresql'
        '''
        logging.debug("Configured to use Postgresql for a database")
        try:
            import pypostgresql
        except ImportError:
            print(WARN+"You must install 'pypostgresql' to use a postgresql database.")
            os._exit(1)
        db_host, db_name, db_user, db_password = self.__db__()
        return 'postgresql+pypostgresql://%s:%s@%s/%s' % (
            db_user, db_password, db_host, db_name,
        )

    def __sqlite__(self):
        ''' SQLite connection string, always save db file to cwd, or in-memory '''
        logging.debug("Configured to use SQLite for a database")
        db_name = os.path.basename(self.config.get("Database", 'name'))
        if 0 == len(db_name):
            db_name = 'rtb'
        return ('sqlite:///%s.db' % db_name) if db_name != ':memory:' else 'sqlite://'

    def __mysql__(self):
        ''' Configure db_connection for MySQL '''
        logging.debug("Configured to use MySQL for a database")
        db_server, db_name, db_user, db_password = self.__db__()
        return 'mysql://%s:%s@%s/%s' % (
            db_user, db_password, db_server, db_name
        )

    def _test_db_connection(self, connection_string):
        ''' Test the connection string to see if we can connect to the database'''
        engine = create_engine(connection_string)
        try:
            connection = engine.connect()
            connection.close()
        except:
            if self.debug:
                logging.exception("Database connection failed")
            logging.critical("Failed to connect to database, check settings")
            os._exit(1)

    def __db__(self):
        ''' Pull db creds and return them url encoded '''
        host = self.config.get("Database", 'host')
        name = self.config.get("Database", 'name')
        user = self.config.get("Database", 'user')
        password = self.config.get("Database", 'password')
        if user == '' or user == 'RUNTIME':
            user = raw_input(PROMPT+"Database User: ")
        if password == '' or password == 'RUNTIME':
            sys.stdout.write(PROMPT+"Database password: ")
            sys.stdout.flush()
            password = getpass.getpass()
        db_host = urllib.quote_plus(host)
        db_name = urllib.quote_plus(name)
        db_user = urllib.quote_plus(user)
        db_password = urllib.quote_plus(password)
        return db_host, db_name, db_user, db_password

