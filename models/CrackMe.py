'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject

class CrackMe(BaseObject):
    
    crackme_name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(1024))
    value = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False, unique=False)
    file_name = Column(Unicode(64), unique=True, nullable=False)
    file_uuid = Column(Unicode(255), unique=True, nullable=False)
    token = Column(Unicode(255), unique=True, nullable=False)
    
    teams = relationship("Team", backref="CrackMe")

    def __repr__(self):
        return ('<CrackMe - name: %s, value: %d>' % (self.crackme_name, self.value))