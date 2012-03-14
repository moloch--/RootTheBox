'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode, Integer
from models import dbsession
from models.BaseGameObject import BaseObject


class CrackMe(BaseObject):
    
    crackme_name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(1024))
    value = Column(Integer, nullable=False)
    file_name = Column(Unicode(64), unique=True, nullable=False)
    file_uuid = Column(Unicode(64), unique=True, nullable=False)
    token = Column(Unicode(255), unique=True, nullable=False)
    
    teams = relationship("Team", backref="CrackMe")

    def __repr__(self):
        return ('<CrackMe - name: %s, value: %d>' % (self.crackme_name, self.value))
    
    @classmethod
    def by_crackme_name(cls, name):
        """ Return the user object whose user name is ``crackme_name`` """
        return dbsession.query(cls).filter_by(crackme_name=name).first() #@UndefinedVariable
    
    @classmethod
    def by_id(cls, crackme_id):
        """ Return the user object whose user name is ``id`` """
        return dbsession.query(cls).filter_by(id=crackme_id).first() #@UndefinedVariable
    
    