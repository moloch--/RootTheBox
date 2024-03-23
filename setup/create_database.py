# -*- coding: utf-8 -*-
"""
@author: moloch

    Copyright 2013

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


from models import engine
from models.BaseModels import DatabaseObject


def create_tables(sqla_engine, sqla_metadata, echo=False):
    """Create all the tables"""
    setattr(sqla_engine, "echo", echo)
    sqla_metadata.create_all(sqla_engine)


# Get the SQLAlchemy metadata object
metadata = DatabaseObject.metadata

# Create secondary tables
# Import your models here
from models.Box import Box
from models.Category import Category
from models.Corporation import Corporation
from models.EmailToken import EmailToken
from models.FileUpload import FileUpload
from models.Flag import Flag
from models.FlagAttachment import FlagAttachment
from models.FlagChoice import FlagChoice
from models.GameLevel import GameLevel
from models.Hint import Hint
from models.IpAddress import IpAddress
from models.MarketItem import MarketItem
from models.Notification import Notification
from models.PasswordToken import PasswordToken
from models.PasteBin import PasteBin
from models.Penalty import Penalty
from models.Permission import Permission
from models.RegistrationToken import RegistrationToken
from models.Relationships import *
from models.SourceCode import SourceCode
from models.Swat import Swat
from models.Team import Team
from models.Theme import Theme, ThemeFile
from models.User import User
from models.WallOfSheep import WallOfSheep
