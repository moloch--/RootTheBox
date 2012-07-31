# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode, Integer
from models import dbsession
from models.BaseGameObject import BaseObject


class CrackMe(BaseObject):

    crack_me_name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(1024))
    value = Column(Integer, nullable=False)
    file_name = Column(Unicode(64), unique=True, nullable=False)
    uuid = Column(Unicode(64), unique=True, nullable=False)
    content = Column(Unicode(64), nullable=False)
    token = Column(Unicode(255), unique=True, nullable=False)

    teams = relationship("Team", backref="CrackMe")

    @classmethod
    def by_crackme_name(cls, name):
        ''' Return the user object whose user name is "crackme_name" '''
        return dbsession.query(cls).filter_by(crackme_name=unicode(name)).first()

    @classmethod
    def by_id(cls, crackme_id):
        ''' Return the user object whose user name is "id" '''
        return dbsession.query(cls).filter_by(id=unicode(crackme_id)).first()

    def __repr__(self):
        return ('<CrackMe - name: %s, value: %d>' % (self.crackme_name, self.value))
