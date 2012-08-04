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

import logging

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.Box import Box
from models.BaseGameObject import BaseObject


class Team(BaseObject):
    ''' Team definition '''

    name = Column(Unicode(64), unique=True, nullable=False)
    motto = Column(Unicode(255))
    members = relationship("User", backref="Team")
    listen_port = Column(Integer, unique=True, nullable=False)
    files = relationship("FileUpload", backref=backref("Team", lazy="dynamic"))
    money = Column(Integer, default=0, nullable=False)

    @classmethod
    def by_team_name(cls, team_name):
        ''' Return the team object based on "team_name" '''
        return dbsession.query(cls).filter_by(team_name=unicode(team_name)).first()  

    @classmethod
    def by_team_id(cls, team_id):
        ''' Return the team object based one id '''
        return dbsession.query(cls).filter_by(id=team_id).first()  

    @classmethod
    def get_all(cls):
        ''' Returns all team objects '''
        return dbsession.query(cls).all()  

    @property
    def crack_me(self):
        ''' Returns the current crack me '''
        return dbsession.query(CrackMe).filter_by(id=self.crack_me_id).first()  

    @property
    def pastes(self):
        ''' Returns all of the pastes the team has '''
        pastes = []
        for user in self.members:
            pastes += user.pastes
        pastes.sort(key=lambda paste: paste.created)
        return pastes

    @property
    def boxes(self):
        ''' Returns a list of box object controlled by the team members '''
        boxes = []
        for user in self.members:
            boxes += user.controlled_boxes
        return boxes

    def file_by_file_name(self, file_name):
        ''' Return file object based on file_name '''
        return files.filter_by(file_name=file_name).first()

    def file_by_uuid(self, uuid):
        ''' Return file object based on uuid '''
        return files.filter_by(uuid=uuid).first()

    def solved_crack_me(self):
        ''' Increments crack_me id '''
        self.crack_me_id += 1

    def is_controlling(self, box):
        ''' Returns a boolean based on if the team has control of a box '''
        return True if box in self.boxes else False

    def __repr__(self):
        return ('<Team - name: %s, score: %d>' % (self.team_name, self.score)).encode('utf-8')

    def __str__(self):
        return unicode(self.name)

    def __radd__(self, other):
        return self.money + other
