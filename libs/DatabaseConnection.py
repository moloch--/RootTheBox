# -*- coding: utf-8 -*-
"""
Created on Sep 20, 2012

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
"""
# pylint: disable=unused-wildcard-import,unused-variable


import os
import logging
import sys
import getpass
import codecs

from builtins import object
from libs.ConsoleColors import *

try:
    from urllib.parse import quote, quote_plus
except ImportError:
    from urllib import quote, quote_plus
from sqlalchemy import create_engine
from tornado.options import options


class DatabaseConnection(object):
    def __init__(
        self,
        database,
        hostname="",
        port="",
        username="",
        password="",
        dialect="",
        ssl_ca="",
    ):
        self.database = database
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.dialect = dialect
        self.ssl_ca = ssl_ca

    def __str__(self):
        """Construct the database connection string"""
        if self.dialect == "sqlite":
            db_conn = self._sqlite()
        elif self.dialect.startswith("postgres"):
            db_conn = self._postgresql()
        elif self.dialect == "mysql":
            db_conn = self._mysql()
        else:
            raise ValueError("Database dialect not supported")
        self._test_connection(db_conn)
        return db_conn

    def _postgresql(self):
        """
        Configured to use postgresql, there is no built-in support
        for postgresql so make sure we can import the 3rd party
        python lib 'pypostgresql'
        """
        logging.debug("Configured to use Postgresql for a database")
        try:
            import pypostgresql
        except ImportError:
            print(WARN + "You must install 'pypostgresql'")
            os._exit(1)
        db_host, db_name, db_user, db_password = self._db_credentials()
        postgres = "postgresql+pypostgresql://%s:%s@%s/%s" % (
            db_user,
            db_password,
            db_host,
            db_name,
        )
        if self._test_connection(postgres):
            return postgres
        else:
            logging.fatal("Cannot connect to database with any available driver")
            os._exit(1)

    def _sqlite(self):
        """
        SQLite connection string, always save db file to cwd, or in-memory
        """
        logging.debug("Configured to use SQLite for a database")
        db_name = self.database
        if not len(db_name):
            db_name = "rootthebox.db"
        if not db_name.endswith(".db"):
            db_name = "%s.db" % db_name
        if os.path.exists("files/%s" % db_name):
            path = "sqlite:///files/%s" % db_name
            logging.debug("Found rootthebox database at: %s" % path)
        elif os.path.exists(db_name):
            path = "sqlite:///%s" % db_name
            logging.debug("Found rootthebox database at: %s" % path)
        else:
            if "files" in db_name:
                path = "sqlite:///%s" % db_name
            else:
                path = "sqlite:///files/%s" % db_name
            logging.debug("Created rootthebox database at: %s" % path)
        return path

    def _mysql(self):
        """Configure db_connection for MySQL"""
        logging.debug("Configured to use MySQL for a database")
        db_server, db_name, db_user, db_password = self._db_credentials()
        db_charset = "utf8mb4"
        db_connection = "%s:%s@%s/%s?charset=%s" % (
            db_user,
            db_password,
            db_server,
            db_name,
            db_charset,
        )

        if self.ssl_ca != "":
            db_connection = db_connection + "&ssl_ca=" + self.ssl_ca

        codecs.register(
            lambda name: codecs.lookup("utf8") if name == "utf8mb4" else None
        )
        __mysql = "mysql://%s" % db_connection
        __mysqlclient = "mysql+mysqldb://%s" % db_connection
        __pymysql = "mysql+pymysql://%s" % db_connection
        __mysqlconnector = "mysql+mysqlconnector://%s" % db_connection
        if self._test_connection(__mysql):
            return __mysql
        elif self._test_connection(__mysqlclient):
            return __mysqlclient
        elif self._test_connection(__pymysql):
            return __pymysql
        elif self._test_connection(__mysqlconnector):
            return __mysqlconnector
        else:
            logging.fatal(
                "Cannot connect to database with any available driver. Verify correct username & password in rootthebox.cfg and db dependencies."
            )
            os._exit(1)

    def _test_connection(self, connection_string):
        """
        Test the connection string to see if we can connect to the database
        """
        try:
            engine = create_engine(connection_string)
            connection = engine.connect()
            connection.close()
            return True
        except Exception as e:
            if options.debug:
                logging.exception("Database connection failed: %s" % e)
            return False

    def _db_credentials(self):
        """Pull db creds and return them url encoded"""
        if self.password == "" or self.password == "RUNTIME":
            sys.stdout.write(PROMPT + "Database password: ")
            sys.stdout.flush()
            self.password = getpass.getpass()
        elif self.password == "ENV":
            self.password = os.environ["sql_password"]
        db_host = quote(self.hostname)
        db_name = quote(self.database)
        db_user = quote(self.username)
        db_password = quote_plus(self.password)
        if "@" in db_password:
            logging.warning(
                "%sWARNING:%s Using the '@' symbol in your database password can cause login issues with SQL Alchemy.%s"
                % (WARN + bold + R, W, WARN)
            )
        return db_host, db_name, db_user, db_password
