'''
Created on Mar 15, 2012

@author: moloch
'''

from models import dbsession
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

    @classmethod
    def by_user_name(cls, uuid):
        """ Return the user object whose user name is ``uuid`` """
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first() #@UndefinedVariable

    @classmethod
    def by_file_name(cls, file_name):
        """ Return the user object whose user name is ``file_name`` """
        return dbsession.query(cls).filter_by(file_name=unicode(file_name)).first() #@UndefinedVariable
