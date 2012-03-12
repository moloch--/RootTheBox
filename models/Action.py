'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column
from sqlalchemy.types import Unicode
from models.BaseGameObject import BaseObject

class Action(BaseObject):
    ''' Action definition '''
    
    description = Column(Unicode(255))
    classification = Column(Unicode(255))
    