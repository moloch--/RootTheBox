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
        elif os.path.exists('RootTheBox/' + cfg_file):
            self.conf = os.path.abspath('RootTheBox/' + cfg_file)
        else:
            logging.critical(
                "No configuration file found at: %s." % self.conf
            )
            os._exit(1)
        self.refresh()

    def refresh(self):
        ''' Refresh config file settings '''
        logging.info('Loading config from: %s' % self.conf)
        self.config = ConfigParser.SafeConfigParser()
        self.config_fp = open(self.conf, 'r')
        self.config.readfp(self.config_fp)
        self.__logging__()

    def save(self):
        ''' Write current config to file '''
        self.config_fp.close()
        fp = open(self.conf, 'w')
        self.config.write(fp)
        fp.close()
        self.refresh()

    def __logging__(self):
        ''' Load network configurations '''
        level = self.config.get("Server", 'logging').lower()
        logger = logging.getLogger()
        logger.setLevel(logging_levels.get(level, logging.NOTSET))

    @property
    def listen_port(self):
        ''' Web app listen port, only read once '''
        return self.config.getint("Server", 'port')

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
        ''' Get domain '''
        return self.config.get("Server", 'domain').replace(' ', '')

    @property
    def default_theme(self):
        return self.config.get("Server", "theme")

    @default_theme.setter
    def default_theme(self, value):
        self.config.set("Server", "theme", value)

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
        return self.config.getint("Game", 'bot_reward')

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
        self.config.set("Game",
            'bot_reward_interval', str(value))
    
    @property
    def bribe_cost(self):
        ''' Base amount of a SWAT bribe '''
        return self.config.getint("Game", 'bribe_cost')

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
        return self.config.getint("Cache", 'session_age')
    
    @property
    def session_regeneration_interval(self):
        return self.config.getint("Cache", 'session_regeneration_interval')

    @property
    def admin_ips(self):
        ''' Load security configurations '''
        ips = self.config.get("Security", 'admin_ips')
        ips = ips.replace(" ", "").split(',')
        ips.append('127.0.0.1')
        ips.append('::1')
        return tuple(set(ips))
    
    @property
    def max_password_length(self):
        return self.config.getint("Game", 'max_password_length')

    @max_password_length.setter
    def max_password_length(self, value):
        assert isinstance(value, int)
        self.config.set("Game", 'max_password_length', str(value))

    @property
    def password_upgrade_cost(self):
        return self.config.getint("Game", 'password_upgrade_cost')

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
    def db_connection(self):
        ''' Db connection string, only read once '''
        db = self.config.get("Database", 'db').lower()
        if db == 'sqlite':
            return self.__sqlite__()
        else:
            return self.__mysql__()

    def __sqlite__(self):
        ''' SQLite connection string '''
        logging.debug("Configured to use SQLite for a database")
        return 'sqlite:///rootthebox.db'

    def __mysql__(self):
        ''' Configure db_connection for MySQL '''
        logging.debug("Configured to use MySQL for a database")
        server = self.config.get("Database", 'server')
        name = self.config.get("Database", 'name')
        user = self.config.get("Database", 'user')
        if user == '' or user == 'RUNTIME':
            user = raw_input(PROMPT + "Database User: ")
        password = self.config.get("Database", 'password')
        if password == '' or password == 'RUNTIME':
            sys.stdout.write(PROMPT + "Database password: ")
            sys.stdout.flush()
            password = getpass.getpass()
        db_server = urllib.quote_plus(server)
        db_name = urllib.quote_plus(name)
        db_user = urllib.quote_plus(user)
        db_password = urllib.quote_plus(password)
        return 'mysql://%s:%s@%s/%s' % (
            db_user, db_password, db_server, db_name
        )

