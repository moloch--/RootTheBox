# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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


from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer, Boolean
from sqlalchemy.orm import relationship, backref
from models import dbsession
from models.BaseGameObject import BaseObject


class GameSettings(BaseObject):
    ''' Game Level definition '''

    # General settings
    profile_name = Column(Unicode(32), unique=True, nullable=False, default=u"Root the Box Default")
    is_active = Column(Boolean, nullable=False, default=False)

    # Botnet settings
    bot_reward = Column(Integer, nullable=False, default=300)

    # Black market upgrade settings
    password_upgrade_cost = Column(Integer, nullable=False, default=1500)
    bribe_cost = Column(Integer, nullable=False, default=1500)

    #first_login_message = Column(Unicode(4096), default=u"Welcome to Root the Box")

    @classmethod
    def get_active(cls):
        ''' Return first active settings '''
        settings = dbsession.query(cls).filter_by(is_active=True).first()
        assert(settings is not None)
        return settings
