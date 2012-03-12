'''
Created on Mar 12, 2012

@author: moloch
'''

from hashlib import md5
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.types import Unicode, Integer
from models import dbsession
from models.BaseGameObject import BaseObject

class User(BaseObject):
    """ User definition """

    user_name = Column(Unicode(64), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    team_id = Column(Integer, ForeignKey('team.id'))
    
    _password = Column('password', Unicode(128))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password', self.__class__._hash_password(password))
    ))
    
    def __repr__(self):
        return ('<User: %s, display=%s, email=%s>' % (self.user_name, self.display_name, self.email_address)).encode('utf-8')

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
    def groups_names(self):
        """Return a list with all groups names the user is a member of."""
        return [g.group_name for g in self.groups]
    
    def in_group(self, group):
        """Return True if ``group`` is in groups_names."""
        return True if group in self.groups_names else False

    @classmethod
    def by_email_address(cls, email_address):
        """Return the user object whose email address is ``email_address``."""
        return dbsession.query(cls).filter_by(email_address=email_address).first() #@UndefinedVariable

    @classmethod
    def by_user_name(cls, user_name):
        """Return the user object whose user name is ``user_name``."""
        return dbsession.query(cls).filter_by(user_name=user_name).first() #@UndefinedVariable

    @classmethod
    def _hash_password(cls, password):
        # Make sure password is a str because we cannot hash unicode objects
        if isinstance(password, unicode): password = password.encode('utf-8')
        md5Hash = md5()
        md5Hash.update()
        password = md5Hash.hexdigest()
        # Make sure the hashed password is a unicode object at the end of the
        # process because SQLAlchemy _wants_ unicode objects for Unicode cols
        if not isinstance(password, unicode): 
            password = password.decode('utf-8')
        return password

    def validate_password(self, password):
        """Check the password against existing credentials."""
        input_hash = md5()
        if isinstance(password, unicode): 
            password = password.encode('utf-8')
        input_hash.update(password)
        return self.password == input_hash.hexdigest()
