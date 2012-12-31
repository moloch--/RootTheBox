# -*- coding: utf-8 -*-
'''
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
'''


from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Integer
from sqlalchemy.orm import sessionmaker
from models.BaseGameObject import BaseObject
from libs.ConfigManager import ConfigManager

metadata = BaseObject.metadata

config = ConfigManager.Instance()
db_connection = 'mysql://%s:%s@%s/%s' % (
    config.db_user, config.db_password, config.db_server, config.db_name
)

# Setup the database session
engine = create_engine(db_connection)
setattr(engine, 'echo', config.log_sql)
Session = sessionmaker(bind=engine, autocommit=True)
dbsession = Session(autoflush=True)

team_to_box = Table('team_to_box', BaseObject.metadata,
    Column('team_id', Integer, ForeignKey('team.id'), nullable=False),
    Column('box_id', Integer, ForeignKey('box.id'), nullable=False)
)

team_to_item = Table('team_to_item', BaseObject.metadata,
    Column('team_id', Integer, ForeignKey('team.id'), nullable=False),
    Column('item_id', Integer, ForeignKey('market_item.id'), nullable=False)
)

team_to_source_code = Table('team_to_souce_code', BaseObject.metadata,
    Column('team_id', Integer, ForeignKey('team.id'), nullable=False),
    Column('souce_code_id', Integer, ForeignKey('source_code.id'), nullable=False)
)

team_to_flag = Table('team_to_flag', BaseObject.metadata,
    Column('team_id', Integer, ForeignKey('team.id'), nullable=False),
    Column('flag_id', Integer, ForeignKey('flag.id'), nullable=False)
)

team_to_game_level = Table('team_to_game_level', BaseObject.metadata,
    Column('team_id', Integer, ForeignKey('team.id'), nullable=False),
    Column('game_level_id', Integer, ForeignKey('game_level.id'), nullable=False)
)

snapshot_to_snapshot_team = Table('snapshot_to_snapshot_team', BaseObject.metadata,
    Column('snapshot_id', Integer, ForeignKey('snapshot.id'), nullable=False),
    Column('snapshot_team_id', Integer, ForeignKey('snapshot_team.id'), nullable=False)
)

snapshot_team_to_flag = Table('snapshot_team_to_flag', BaseObject.metadata,
    Column('snapshot_team_id', Integer, ForeignKey('snapshot_team.id'), nullable=False),
    Column('flag_id', Integer, ForeignKey('flag.id'), nullable=False)
)

snapshot_team_to_game_level = Table('snapshot_team_to_game_level', BaseObject.metadata,
    Column('snapshot_team_id', Integer, ForeignKey('snapshot_team.id'), nullable=False),
    Column('gam_level_id', Integer, ForeignKey('game_level.id'), nullable=False)
)

# import models
from models.Box import Box
from models.PasteBin import PasteBin
from models.Permission import Permission
from models.Team import Team
from models.User import User
from models.FileUpload import FileUpload
from models.WallOfSheep import WallOfSheep
from models.Flag import Flag
from models.Notification import Notification
from models.Corporation import Corporation
from models.GameLevel import GameLevel
from models.Theme import Theme
from models.RegistrationToken import RegistrationToken
from models.MarketItem import MarketItem
from models.IpAddress import IpAddress
from models.Snapshot import Snapshot
from models.SnapshotTeam import SnapshotTeam
from models.SourceCode import SourceCode

# calling this will create the tables at the database
create_tables = lambda: (setattr(engine, 'echo', config.log_sql), metadata.create_all(engine))

# Bootstrap the database with some shit
def boot_strap():
    import setup.bootstrap
