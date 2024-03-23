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


from models.BaseModels import DatabaseObject


def create_tables(sqla_engine, sqla_metadata, echo=False):
    """Create all the tables"""
    setattr(sqla_engine, "echo", echo)
    sqla_metadata.create_all(sqla_engine)


# Get the SQLAlchemy metadata object
metadata = DatabaseObject.metadata

# Create secondary tables
# Import your models here
from models.Relationships import *
