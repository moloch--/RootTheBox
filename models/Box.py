'''
Created on Mar 11, 2012

@author: moloch
'''

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.BaseGameObject import BaseObject
from models import association_table

class Box(BaseObject):
    ''' Box definition '''
    
    box_name = Column(Unicode(64), unique=True, nullable=False)
    ip_address = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(1024))
    root_key = Column(Unicode(255), unique=True, nullable=False)
    root_value = Column(Integer, nullable=False)
    user_key = Column(Unicode(255), unique=True, nullable=False)
    user_value = Column(Integer, nullable=False)
    users = relationship("User", secondary=association_table, backref="Box")
    
    def __repr__(self):
        return ('<Box: name=%s, root_value=%d, user_value=%d>' % (self.box_name, self.root_value, self.user_value)).encode('utf-8')

    def __unicode__(self):
        return self.box_name
    
    @property
    def teams(self):
        pass

    @classmethod
    def get_all(cls):
        """ Returns a list of all boxes in the database """
        return dbsession.query(cls).all() #@UndefinedVariable

    @classmethod
    def by_box_name(cls, box_name):
        """ Return the box object whose name is ``box_name`` """
        return dbsession.query(cls).filter_by(box_name=unicode(box_name)).first() #@UndefinedVariable
    
    @classmethod
    def by_ip_address(cls, ip_address):
        """ Return the box object whose name is ``box_name`` """
        return dbsession.query(cls).filter_by(ip_address=unicode(ip_address)).first() #@UndefinedVariable