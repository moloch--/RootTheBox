# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

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


import os
import sys
import getpass
import logging
import ConfigParser

from libs import ConsoleColors
from libs.Singleton import Singleton
from libs.HostNetworkConfig import HostNetworkConfig


# .basicConfig must be called prior to ANY call to logging.XXXX so make sure
# this module gets imported prior to any logging!
logging.basicConfig(format='\r[%(levelname)s] %(asctime)s - %(message)s',
                    level=logging.DEBUG)


@Singleton
class ConfigManager(object):
    '''  Central class which handles any user-controlled settings '''

    def __init__(self, cfg_file='rootthebox.cfg'):
        self.cfg_path = os.path.abspath(cfg_file)
        if not (os.path.exists(self.cfg_path) and os.path.isfile(self.cfg_path)):
            logging.critical("No configuration file found at %s, cannot continue." %
                             cfg_path)
            os._exit(1)
        logging.info('Loading config from %s' % self.cfg_path)
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(self.cfg_path, 'r'))
        self.__server__()
        self.__sessions__()
        self.__security__()
        self.__database__()
        self.__recaptcha__()

    def __server__(self):
        ''' Load network configurations '''
        self.listen_port = self.config.getint("Server", 'port')
        self.debug = self.config.getboolean("Server", 'debug')
        self.domain = self.config.get("Server", 'domain')
        self.default_theme = self.config.get("Server", "theme")

    def __sessions__(self):
        self.memcached_server = self.config.get("Sessions", 'memcached')
        self.session_age = self.config.getint("Sessions", 'session_age')
        self.session_regeneration_interval = self.config.getint(
            "Sessions", 'session_regeneration_interval')

    def __security__(self):
        ''' Load security configurations '''
        ips = self.config.get("Security", 'admin_ips', "127.0.0.1").split(',')
        if not '127.0.0.1' in ips:
            ips.append('127.0.0.1')
        self.admin_ips = tuple(ips)
        self.max_password_length = int(
            self.config.get("Security", 'max_password_length'))

    def __recaptcha__(self):
        ''' Loads recaptcha settings '''
        self.recaptcha_enable = self.config.getboolean("Recaptcha", 'enable')
        self.recaptcha_private_key = self.config.get(
            "Recaptcha", 'private_key')

    def __database__(self):
        ''' Loads database connection information '''
        self.db_server = self.config.get("Database", 'server', "localhost")
        self.db_name = self.config.get("Database", 'name', "rootthebox")
        user = self.config.get("Database", 'user', "RUNTIME")
        if user == 'RUNTIME':
            user = raw_input(ConsoleColors.PROMPT + "Database User: ")
        self.db_user = user
        password = self.config.get("Database", 'password', "RUNTIME")
        if password == 'RUNTIME':
            sys.stdout.write(ConsoleColors.PROMPT + "Database ")
            sys.stdout.flush()
            password = getpass.getpass()
        self.db_password = password
