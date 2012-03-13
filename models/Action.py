'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject

class Action(BaseObject):
    ''' Action definition '''
    
    classification = Column(Unicode(255), nullable=False)
    description = Column(Unicode(1024), nullable=False)
    value = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    