'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
import sqlalchemy.orm as orm
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject
from models import dbsession, association_table
import models
import logging
from sqlalchemy.orm import mapper
from sqlalchemy import event
from libs.ScoreUpdate import ScoreUpdate
from libs.WebSocketManager import WebSocketManager
from sqlalchemy.orm import sessionmaker

class Action(BaseObject):
    ''' Action definition '''
    
    classification = Column(Unicode(255), nullable=False)
    description = Column(Unicode(1024), nullable=False)
    value = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return ('<Action - class:%s, user_id:%d>' % (self.classification, self.user_id))
    
    def __radd__(self, other):
        return self.value + other
    
def insert_listener(mapper, connection, target):       
    team = dbsession.query(models.User).filter_by(id=target.user_id).first()
    ws_manager = WebSocketManager.Instance()
    score_update = ScoreUpdate(target.created.strftime("%d%H%M%S"), target.value, team.team_name)
    ws_manager.currentUpdates.append(score_update)
    ws_manager.send_all(score_update)

# attach to all mappers
event.listen(Action, 'after_insert', insert_listener)

