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

class Post(BaseObject):
    ''' Post definition '''
    
    name = Column(Unicode(255), nullable=False)
    contents = Column(Unicode(1024), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return ('<Post - name:%s, user_id:%d>' % (self.name, self.user_id))
    



