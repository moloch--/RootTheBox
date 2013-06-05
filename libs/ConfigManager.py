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
import getpass
import logging
import ConfigParser

from libs.ConsoleColors import *
from libs.Singleton import Singleton


# .basicConfig must be called prior to ANY call to logging.XXXX so make sure
# this module gets imported prior to any logging!
logging.basicConfig(
    format='\r[%(levelname)s] %(asctime)s - %(message)s', level=logging.DEBUG
)


@Singleton
class ConfigManager(object):
    ''' Central class which handles any user-controlled settings '''

    def __init__(self, cfg_file='rootthebox.cfg'):
        if os.path.exists(cfg_file) and os.path.isfile(cfg_file):
            self.conf = os.path.abspath(cfg_file)
        elif os.path.exists('RootTheBox/' + cfg_file):
            self.conf = os.path.abspath('RootTheBox/' + cfg_file)
        else:
            logging.critical(
                "No configuration file found at: %s." % self.conf
            )
            os._exit(1)
        logging.info('Loading config from: %s' % self.conf)
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(self.conf, 'r'))
        self.__server__()
        self.__sessions__()
        self.__security__()
        self.__database__()
        self.__recaptcha__()
        self.__upgrades__()
        self.__botnets__()

    def __server__(self):
        ''' Load network configurations '''
        self.listen_port = self.config.getint("Server", 'port')
        log_level = self.config.get("Server", 'logging')
        logger = logging.getLogger()
        if log_level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif log_level.lower() == 'info':
            logger.setLevel(logging.INFO)
        elif log_level.lower() == 'warn':
            logger.setLevel(logging.WARN)
        else:
            sys.stdout.write(WARN + "Logging level has not been set.\n")
            logger.setLevel(logging.NOTSET)
        sys.stdout.flush()
        self.debug = self.config.getboolean("Server", 'debug')
        self.domain = self.config.get("Server", 'domain').replace(' ', '')
        self.default_theme = self.config.get("Server", "theme")
        self.cache_files = self.config.getboolean("Server", "cache_files")

    def __sessions__(self):
        ''' Session settings '''
        self.memcached_server = self.config.get("Sessions", 'memcached')
        self.session_age = self.config.getint("Sessions", 'session_age')
        self.session_regeneration_interval = self.config.getint("Sessions",
            'session_regeneration_interval'
        )

    def __security__(self):
        ''' Load security configurations '''
        ips = self.config.get("Security", 'admin_ips', "127.0.0.1").replace(" ", "")
        ips = ips.split(',')
        if not '127.0.0.1' in ips:
            ips.append('127.0.0.1')
        self.admin_ips = tuple(ips)
        self.max_password_length = self.config.getint(
            "Security", 'max_password_length'
        )

    def __upgrades__(self):
        self.password_upgrade = self.config.getint(
            "Upgrades", 'password_upgrade'
        )
        self.bribe_base_price = self.config.getint(
            "Upgrades", 'bribe_base_price'
        )

    def __botnets__(self):
        self.bot_reward = self.config.getint(
            "Botnets", 'reward'
        )
        self.bot_sql = self.config.getboolean(
            "Botnets", 'bot_sql'
        )

    def __recaptcha__(self):
        ''' Loads recaptcha settings '''
        self.recaptcha_enable = self.config.getboolean("Recaptcha", 'enable')
        self.recaptcha_private_key = self.config.get(
            "Recaptcha", 'private_key'
        )

    def __database__(self):
        ''' Loads database connection information '''
        self.log_sql = self.config.getboolean("Database", 'log_sql')
        self.db_server = self.config.get("Database", 'server', "localhost")
        self.db_name = self.config.get("Database", 'name', "rootthebox")
        user = self.config.get("Database", 'user', "RUNTIME")
        if user == 'RUNTIME':
            user = raw_input(PROMPT + "Database User: ")
        self.db_user = user
        password = self.config.get("Database", 'password', "RUNTIME")
        if password == 'RUNTIME':
            sys.stdout.write(PROMPT + "Database ")
            sys.stdout.flush()
            password = getpass.getpass()
        self.db_password = password
