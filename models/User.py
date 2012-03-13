'''
Created on Mar 12, 2012

@author: moloch
'''

from hashlib import md5
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession, Team
from models.BaseGameObject import BaseObject

class User(BaseObject):
    """ User definition """

    user_name = Column(Unicode(64), unique=True, nullable=False)
    display_name = Column(Unicode(64))
    team_id = Column(Integer, ForeignKey('team.id'))
    dirty = Column(Boolean)
    score_cache = Column(Integer)
    actions = relationship("Action", backref=backref("User", lazy="joined"), cascade="all, delete-orphan")
    
    _password = Column('password', Unicode(128))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password', self.__class__._hash_password(password))
    ))
    
    def __repr__(self):
        return ('<User: %s, display=%s, team_id=%d>' % (self.user_name, self.display_name, self.team_id)).encode('utf-8')

    def __unicode__(self):
        return self.display_name or self.user_name

    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        permissions = set()
        for group in self.groups: permissions = permissions | set(group.permissions)
        return permissions

    @property
    def permissions_names(self):
        """Return a list with all permissions names granted to the user."""
        return [p.permission_name for p in self.permissions]
        
    def has_permission(self, permission):
        """Return True if ``permission`` is in permissions_names."""
        return True if permission in self.permissions_names else False

    @property
    def team_name(self):
        """ Return a list with all groups names the user is a member of """
        if self.team_id == None:
            return None
        else:
            team = dbsession.query(Team).filter_by(id=self.team_id).first() #@UndefinedVariable
            return team.team_name

    @classmethod
    def by_user_name(cls, user_name):
        """ Return the user object whose user name is ``user_name`` """
        return dbsession.query(cls).filter_by(user_name=user_name).first() #@UndefinedVariable

    @classmethod
    def _hash_password(cls, password):
        ''' Hashes the password using insecure Md5 :D '''
        if isinstance(password, unicode): 
            password = password.encode('utf-8')
        md5Hash = md5()
        md5Hash.update(password)
        password = md5Hash.hexdigest()
        if not isinstance(password, unicode): 
            password = password.decode('utf-8')
        return password

    def validate_password(self, password):
        """ Check the password against existing credentials """
        input_hash = md5()
        if isinstance(password, unicode): 
            password = password.encode('utf-8')
        input_hash.update(password)
        return self.password == input_hash.hexdigest()
