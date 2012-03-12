'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.BaseGameObject import BaseObject

class Team(BaseObject):
    """ Team definition """

    team_name = Column(Unicode(64), unique=True, nullable=False)
    motto = Column(Unicode(255))
    score = Column(Integer)
    members = relationship("members")

    # Relations
    #users = relationship('User', secondary=user_group_table, backref='teams')

    @classmethod
    def by_team_name(cls, team_name):
        """Return the user object whose group name is ``team_name``."""
        return dbsession.query(cls).filter_by(team_name=team_name).first() #@UndefinedVariable

    def __repr__(self):
        return ('<Team: %s, score=%s>'%(self.team_name, self.score)).encode('utf-8')

    def __unicode__(self):
        return self.team_name