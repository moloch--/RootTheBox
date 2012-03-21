'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject
from models import team_challenges, dbsession

class Challenge(BaseObject):
    ''' Challenge definition '''
    
    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(1024), nullable=False)
    token = Column(Unicode(255), nullable=False)
    value = Column(Integer, nullable=False)
    teams = relationship("Team", secondary=team_challenges, backref="Challenge")
   
    @classmethod
    def get_all(cls):
        ''' Returns all challenge objects '''
        return dbsession.query(cls).all() #@UndefinedVariable
 
    @classmethod
    def get_by_id(cls, challenge_id):
        ''' Returns all challenge objects '''
        return dbsession.query(cls).filter_by(id=challenge_id).first() #@UndefinedVariable

    def __repr__(self):
        return ('<Challenge - name:%s, value:%d>' % (self.name, self.value))
    
    def __radd__(self, other):
        return self.value + other


