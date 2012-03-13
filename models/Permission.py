'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy.types import Unicode, Integer
from sqlalchemy import Column, ForeignKey
from models.BaseGameObject import BaseObject

class Permission(BaseObject):
    """ Permission definition """

    permission_name = Column(Unicode(64), unique=True, nullable=False)
<<<<<<< HEAD
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
=======
    description = Column(Unicode(255))

    # Relations
    groups = relationship('Team', secondary=team_permission_table, backref='permission')
>>>>>>> 968d323c0b559c43c2be8a53a890192da6109039

    def __repr__(self):
        return ('<Permission - name: %s, user_id: %d>' % (self.permission_name, self.user_id)).encode('utf-8')

    def __unicode__(self):
        return self.permission_name