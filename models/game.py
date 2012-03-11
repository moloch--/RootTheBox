'''
Created on Mar 11, 2012

@author: moloch
'''

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer, Unicode
from models import dbsession, DeclarativeBase

class Action(DeclarativeBase):
    ''' Action definition '''
    
    __tablename__ = 'actions'
    
    id = Column(Integer, primary_key=True) #@ReservedAssignment
    description = Column(Unicode(255))
    classification = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

class Box(DeclarativeBase):
    ''' Box definition '''
    
    __tablename__ = 'boxes'
    
    # Columns
    id = Column(Integer, primary_key=True) #@ReservedAssignment
    box_name = Column(Unicode(64), unique=True, nullable=False)
    ip_address = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(255))
    root_key = Column(Unicode(255), unique=True, nullable=False)
    root_value = Column(Integer)
    user_key = Column(Unicode(255), unique=True, nullable=False)
    user_value = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    
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