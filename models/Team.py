'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.BaseGameObject import BaseObject

class Team(BaseObject):
    """ Team definition """

    team_name = Column(Unicode(64), unique=True, nullable=False)
    motto = Column(Unicode(255))
    score = Column(Integer, default=0)
    members = relationship("User", backref="Team")
    crack_me_id = Column(Integer, ForeignKey("crack_me.id"), default=1)
    
    @classmethod
    def by_team_name(cls, team_name):
        """ Return the user object whose group name is ``team_name`` """
        return dbsession.query(cls).filter_by(team_name=team_name).first() #@UndefinedVariable

    def next_crack_me(self):
        self.crack_me_id += 1
        
    def __repr__(self):
        return ('<Team - name: %s, score: %d>' % (self.team_name, self.score)).encode('utf-8')

    def __unicode__(self):
        return self.team_name
    
    def __str__(self):
        return unicode(self.team_name)