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

    def __init__(self, cfg_file='rootthebox.cfg'):
        self.filename = cfg_file
        if os.path.exists(cfg_file) and os.path.isfile(cfg_file):
            self.conf = os.path.abspath(cfg_file)
        else:
            sys.stderr.write(WARN+"No configuration file found at: %s." % self.conf)
            os._exit(1)
        self.refresh()
        self.__logging__()

    def __logging__(self):
        ''' Load network configurations '''
        level = self.config.get("Logging", 'console_level').lower()
        logger = logging.getLogger()
        logger.setLevel(logging_levels.get(level, logging.NOTSET))
        if self.config.getboolean("Logging", 'save_logs'):
            file_log = logging.FileHandler('%s' % self.config.get("Logging", 'logfile'))
            logger.addHandler(file_log)
            file_format = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
            file_log.setFormatter(file_format)
            flevel = self.config.get("Logging", 'file_level').lower()
            file_log.setLevel(logging_levels.get(flevel, logging.NOTSET))

    def refresh(self):
        ''' Refresh config file settings '''
        self.config = ConfigParser.SafeConfigParser()
        self.config_fp = open(self.conf, 'r')
        self.config.readfp(self.config_fp)

    def save(self):
        ''' Write current config to file '''
        self.config_fp.close()
        os.rename(self.conf, '%s-%s.old' % (datetime.now(), self.conf))
        fp = open(self.conf, 'w')
        self.config.write(fp)
        fp.close()
        self.refresh()

    @property
    def listen_port(self):
        ''' Web app listen port, only read once '''
        lport = self.config.getint("Server", 'port')
        if not 0 < lport < 65535:
            logging.fatal("Listen port not in valid range: %d" % lport)
            os._exit(1)
        return lport

    @property
    def debug(self):
        ''' Debug mode '''
        return self.config.getboolean("Server", 'debug')

    @debug.setter
    def debug(self, value):
        assert isinstance(value, bool)
        self.config.set("Server", 'debug', str(value))

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
            logging.warn("Possible misconfiguration 'domain' is set to 'localhost'")
        return _domain

    @property
    def public_teams(self):
        ''' Allow new users to create their own teams '''
        return self.config.getboolean("Game", 'public_teams')

    @property
    def restrict_registration(self):
        ''' Enable/disable registration tokens '''
        return self.config.getboolean("Game", 'restrict_registration')

    @property
    def default_theme(self):
        return self.config.get("Server", "theme")

    @property
    def cache_files(self):
        ''' Cache small files in memcached, only read once '''
        return self.config.getboolean("Server", "cache_files")

    @property
    def game_name(self):
        return self.config.get("Game", 'game_name')[:16]

    @game_name.setter
    def game_name(self, value):
        assert isinstance(value, basestring)
        self.config.set("Game", 'game_name', value[:16])

    @property
    def bot_reward(self):
        ''' Reward per bot per interval '''
        return abs(self.config.getint("Game", 'bot_reward'))

    @bot_reward.setter
    def bot_reward(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'bot_reward', str(value))

    @property
    def bot_reward_interval(self):
        ''' Check bots every so many minutes '''
        conf = self.config.getint("Game", 'bot_reward_interval')
        return  60000 * conf

    @bot_reward_interval.setter
    def bot_reward_interval(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'bot_reward_interval', str(value))
    
    @property
    def bribe_cost(self):
        ''' Base amount of a SWAT bribe '''
        return abs(self.config.getint("Game", 'bribe_cost'))

    @bribe_cost.setter
    def bribe_cost(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'bribe_cost', str(value))

    @property
    def history_snapshot_interval(self):
        conf = self.config.getint("Game", 'history_snapshot_interval')
        return 60000 * conf

    @history_snapshot_interval.setter
    def history_snapshot_interval(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'history_snapshot_interval', str(value))

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
    def max_password_length(self):
        return abs(self.config.getint("Game", 'max_password_length'))

    @max_password_length.setter
    def max_password_length(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'max_password_length', str(value))

    @property
    def password_upgrade_cost(self):
        return abs(self.config.getint("Game", 'password_upgrade_cost'))

    @password_upgrade_cost.setter
    def password_upgrade_cost(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'password_upgrade_cost', str(value))

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
    def log_sql(self):
        ''' This value is only read once, no setter '''
        return self.config.getboolean("Database", 'orm_sql')

    @property
    def bot_sql(self):
        ''' This value is only read once, no setter '''
        return self.config.getboolean("Database", 'bot_sql')

    @property
    def enable_ssl(self):
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

    @property 
    def db_connection(self):
        ''' Db connection string, only read once '''
        db = self.config.get("Database", 'db').lower().strip()
        if db == 'sqlite':
            return self.__sqlite__()
        elif db == 'postgresql':
            return self.__postgresql__()
        else:
            return self.__mysql__()

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

