'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject
from models import dbsession, association_table

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
