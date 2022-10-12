# -*- coding: utf-8 -*-
"""
Created on Mar 12, 2012

@author: moloch

    Copyright 2012

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

import re

from builtins import object
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base


class _DatabaseObject(object):

    """All game objects inherit from this object"""

    @declared_attr
    def __tablename__(self):
        """Converts name from camel case to snake case"""
        name = self.__name__
        return name[0].lower() + re.sub(
            r"([A-Z])", lambda letter: "_" + letter.group(0).lower(), name[1:]
        )

    id = Column(Integer, primary_key=True)  # lint:ok
    created = Column(DateTime, default=datetime.now)


# Create an instance called "BaseObject"
DatabaseObject = declarative_base(cls=_DatabaseObject)
