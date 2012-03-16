'''
Created on Mar 15, 2012

@author: moloch
'''

from sqlalchemy.types import Unicode, Integer
from sqlalchemy import Column, ForeignKey
from models.BaseGameObject import BaseObject

class FileUpload(BaseObject):
    
    file_name = Column(Unicode(255), nullable=False)
    content = Column(Unicode(255))
    uuid = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(1024))
    byte_size = Column(Integer)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    
    def __repr__(self):
        return ('<File - name: %s, type: %s>' % (self.file_name, self.content))
