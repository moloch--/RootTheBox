'''
Created on Mar 12, 2012

@author: moloch
'''

import re
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base

class BaseGameObject(object):
    ''' All game objects inherit from this object '''
        
    @declared_attr
    def __tablename__(self):
        ''' Converts name from camel case to snake case '''
        name = self.__name__
        return (
                name[0].lower() +
                re.sub(r'([A-Z])',
                lambda letter: "_" + letter.group(0).lower(), name[1:])
        )
        
    id = Column(Integer, primary_key=True) #@ReservedAssignment
    created = Column(DateTime, default=datetime.now)

# Create an instance called "BaseObject"
BaseObject = declarative_base(cls=BaseGameObject)