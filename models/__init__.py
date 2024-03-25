# -*- coding: utf-8 -*-
"""
Created on Sep 12, 2012

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

import logging
import time
from builtins import str
from contextlib import contextmanager

from msal import ConfidentialClientApplication
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tornado.options import options

from libs.ConsoleColors import *
from libs.DatabaseConnection import DatabaseConnection

if options.log_sql:

    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.setLevel(logging.INFO)

    # This benchmarks the amount of time spent querying the database
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        color = R if total > 0.01 else BLU
        logging.debug("Total query time: %s%s%f%s" % (bold, color, total, W))


db_connection = DatabaseConnection(
    database=options.sql_database,
    hostname=options.sql_host,
    port=options.sql_port,
    username=options.sql_user,
    password=options.sql_password,
    dialect=options.sql_dialect,
    ssl_ca=options.sql_sslca,
)

if options.auth == "azuread":
    azuread_app = ConfidentialClientApplication(
        options.client_id,
        authority="https://login.microsoftonline.com/" + options.tenant_id,
        client_credential=options.client_secret,
    )
else:
    azuread_app = None

### Setup the database session
engine = create_engine(str(db_connection), pool_pre_ping=True)
session_maker = sessionmaker(bind=engine)
_Session = scoped_session(session_maker)
def StartSession():
    return _Session(autoflush=True)

dbsession = StartSession()


chatsession = None
if options.rocketchat_admin:
    try:
        logging.info("Attempting RocketChat connection...")
        from libs.ChatManager import ChatManager

        chatsession = ChatManager(
            username=options.rocketchat_admin,
            password=options.rocketchat_password,
            server_url=options.chat_url,
        )
        logging.info("RocketChat connection established...")
    except Exception as e:
        chatsession = None
        logging.error("RocketChat connection failed.")
        logging.error(str(e))


@contextmanager
def cxt_dbsession():
    """Provide a transactional scope around a series of operations."""
    session = StartSession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Avoids mapper issues
from models.Box import Box
from models.Corporation import Corporation
from models.FileUpload import FileUpload
from models.Flag import Flag
from models.FlagAttachment import FlagAttachment
from models.GameLevel import GameLevel
from models.Hint import Hint
from models.IpAddress import IpAddress
from models.MarketItem import MarketItem
from models.Notification import Notification
from models.PasteBin import PasteBin
from models.Permission import Permission
from models.RegistrationToken import RegistrationToken
from models.SourceCode import SourceCode
from models.Swat import Swat
from models.Team import Team
from models.Theme import Theme, ThemeFile
from models.User import User
from models.WallOfSheep import WallOfSheep
