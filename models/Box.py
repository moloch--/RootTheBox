'''
Created on Mar 11, 2012

@author: moloch
'''

from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.BaseGameObject import BaseObject

class Box(BaseObject):
    ''' Box definition '''
    
    box_name = Column(Unicode(64), unique=True, nullable=False)
    ip_address = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(255))
    root_key = Column(Unicode(255), unique=True, nullable=False)
    root_value = Column(Integer, nullable=False)
    user_key = Column(Unicode(255), unique=True, nullable=False)
    user_value = Column(Integer, nullable=False)
    
    def __repr__(self):
        return ('<Box: name=%s, root_value=%d, user_value=%d>' % (self.box_name, self.root_value, self.user_value)).encode('utf-8')

    def __unicode__(self):
        return self.box_name
    
    @classmethod
    def by_box_name(cls, box_name):
        """Return the box object whose name is ``box_name``."""
        return dbsession.query(cls).filter_by(box_name=box_name).first() #@UndefinedVariable
    
    @classmethod
    def by_ip_address(cls, ip_address):
        """Return the box object whose name is ``box_name``."""
        return dbsession.query(cls).filter_by(ip_address=ip_address).first() #@UndefinedVariable