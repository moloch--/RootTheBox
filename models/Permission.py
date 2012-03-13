'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy.types import Unicode, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Table
from models.BaseGameObject import BaseObject
from models import metadata

team_permission_table = Table('group_permission', metadata,
    Column('user_id', Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

class Permission(BaseObject):
    """ Permission definition """

    permission_name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(255))

    # Relations
    groups = relationship('Team', secondary=team_permission_table, backref='permission')

    # Special methods
    def __repr__(self):
        return ('<Permission: name=%s>' % self.permission_name).encode('utf-8')

    def __unicode__(self):
        return self.permission_name