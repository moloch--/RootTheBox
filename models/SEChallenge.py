'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject
from models import team_challenges, dbsession

class SEChallenge(BaseObject):
    ''' SEChallenge definition '''
    
    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(1024), nullable=False)
    token = Column(Unicode(255), nullable=False)
    value = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=True)
   
    @classmethod
    def get_all(cls):
        ''' Returns all challenge objects '''
        return dbsession.query(cls).all() #@UndefinedVariable
 
    @classmethod
    def get_by_id(cls, se_challenge_id):
        ''' Returns all challenge objects '''
        return dbsession.query(cls).filter_by(id=se_challenge_id).first() #@UndefinedVariable

    @classmethod
    def get_by_level(cls, se_level):
        '''returns a se_challenge found by its level '''
        return dbsession.query(cls).filter_by(level=se_level).first() #@UndefinedVariable

    @classmethod
    def get_lowest(cls):
        ''' Get the lowest level challenge from the db'''
        return dbsession.query(cls).order_by(cls.level).first() #@UndefinedVariable
    
    @classmethod
    def get_highest(cls):
        ''' Gets the highest level se challenge '''
        return dbsession.query(cls).order_by(cls.level.desc()).first()

    def __repr__(self):
        return ('<SEChallenge - name:%s, value:%d>' % (self.name, self.value))
    
    def __radd__(self, other):
        return self.value + other


