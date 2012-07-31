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


# .basicConfig must be called prior to ANY call to logging.XXXX so make sure
# this module gets imported prior to any logging!
logging.basicConfig(format='\r[%(levelname)s] %(asctime)s - %(message)s',
                    level=logging.DEBUG)


@Singleton
class ConfigManager(object):
    '''  Central class which handles any user-controlled settings '''

    def __init__(self):
        self.cfg_path = os.path.abspath("PlanetaryAssaultSystem.cfg")
        if not (os.path.exists(self.cfg_path) and os.path.isfile(self.cfg_path)):
            logging.critical("No configuration file found at %s, cannot continue." %
                             cfg_path)
            os._exit(1)
        logging.info('Loading config from %s' % self.cfg_path)
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(self.cfg_path, 'r'))
        self.__tables__()
        self.__system__()
        self.__network__()
        self.__security__()
        self.__database__()

    def __tables__(self):
        ''' Load rainbow table configurations '''
        self.rainbow_tables = {}
        self.rainbow_tables['LM'] = self.config.get("RainbowTables", 'lm')
        if not os.path.exists(self.rainbow_tables['LM']):
            logging.warn("LM rainbow table directory not found (%s)" %
                         self.rainbow_tables['LM'])
        self.rainbow_tables['NTLM'] = self.config.get("RainbowTables", 'ntlm')
        if not os.path.exists(self.rainbow_tables['NTLM']):
            logging.warn("NTLM rainbow table directory not found (%s)" %
                         self.rainbow_tables['NTLM'])
        self.rainbow_tables['MD5'] = self.config.get("RainbowTables", 'md5')
        if not os.path.exists(self.rainbow_tables['MD5']):
            logging.warn("MD5 rainbow table directory not found (%s)" %
                         self.rainbow_tables['MD5'])

    def __system__(self):
        ''' Load system configurations '''
        threads = self.config.getint("System", 'threads')
        self.max_threads = 1 if threads <= 0 else threads
        self.debug = self.config.getboolean("System", 'debug')

    def __network__(self):
        ''' Load network configurations '''
        self.listen_port = self.config.getint("Network", 'port')

    def __security__(self):
        ''' Load security configurations '''
        ips = self.config.get("Security", 'admin_ips').split(',')
        if not '127.0.0.1' in ips:
            ips.append('127.0.0.1')
        self.admin_ips = tuple(ips)

    def __database__(self):
        ''' Loads database connection information '''
        self.db_server = self.config.get("Database", 'server')
        self.db_name = self.config.get("Database", 'name')
        user = self.config.get("Database", 'user')
        if user == 'RUNTIME':
            user = raw_input(ConsoleColors.PROMPT + "Database User: ")
        self.db_user = user
        password = self.config.get("Database", 'password')
        if password == 'RUNTIME':
            sys.stdout.write(ConsoleColors.PROMPT + "Database ")
            sys.stdout.flush()
            password = getpass.getpass()
        self.db_password = password
