'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode
from models import dbsession, association_table
from models.CrackMe import CrackMe
from models.Box import Box
from models.BaseGameObject import BaseObject

class Team(BaseObject):
    """ Team definition """

    team_name = Column(Unicode(64), unique=True, nullable=False)
    motto = Column(Unicode(255))
    score = Column(Integer, default=0)
    members = relationship("User", backref="Team")
    crack_me_id = Column(Integer, ForeignKey("crack_me.id"), default=1)
    controlled_boxes = relationship("Box", secondary=association_table, backref="Team")
    files = relationship("FileUpload", backref=backref("Team", lazy="dynamic"))
    
    @classmethod
    def by_team_name(cls, team_name):
        """ Return the user object whose group name is ``team_name`` """
        return dbsession.query(cls).filter_by(team_name=unicode(team_name)).first() #@UndefinedVariable
    
    @classmethod
    def get_all(cls):
        return dbsession.query(cls).all() #@UndefinedVariable
    
    @property
    def crack_me(self):
        ''' Returns the current crack me '''
        return dbsession.query(CrackMe).filter_by(id=self.crack_me_id).first() #@UndefinedVariable
    
    def give_control(self, box_name):
        box = Box.by_box_name(unicode(box_name))
        if not self.is_controlling(box.box_name):
            self.controlled_boxes.append(box)
    
    def lost_control(self, box_name):
        if self.is_controlling(Box.by_box_name(box_name)):
            self.controlled_boxes.remove(Box.by_box_name(box_name))
    
    def is_controlling(self, box_name):
        return Box.by_box_name(box_name) in self.controlled_boxes
    
    def solved_crack_me(self):
        self.crack_me_id += 1
        
    def __repr__(self):
        return ('<Team - name: %s, score: %d>' % (self.team_name, self.score)).encode('utf-8')

    def __unicode__(self):
        return self.team_name
    
    def __str__(self):
        return unicode(self.team_name)