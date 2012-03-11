# -*- coding: utf-8 -*-
"""Authentication related models."""

from os import urandom
#from hashlib import md5
from hashlib import sha256
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.types import DateTime, Integer, Unicode
from models import dbsession, DeclarativeBase, metadata

#{ Association tables
# This is the association table for the many-to-many relationship between groups and members.
user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

# This is the association table for the many-to-many relationship between groups and permissions.
group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('groups.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

# The authentication models
class User(DeclarativeBase):
    """User definition."""
    __tablename__ = 'users'

    # Columns
    id = Column(Integer, primary_key=True) #@ReservedAssignment
    user_name = Column(Unicode(64), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    email_address = Column(Unicode(255), unique=True, nullable=False)
    created = Column(DateTime, default=datetime.now)
    
    _password = Column('password', Unicode(128))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password', self.__class__._hash_password(password))
    ))
    
    # Special methods
    def __repr__(self):
        return ('<User: %s, display=%s, email=%s>'%(self.user_name, self.display_name, self.email_address)).encode('utf-8')

    def __unicode__(self):
        return self.display_name or self.user_name

    # Getters and setters
    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        permissions = set()
        for g in self.groups: permissions = permissions | set(g.permissions)
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
        salt = sha256()
        salt.update(urandom(192))
        secure_hash = sha256()
        secure_hash.update(password + salt.hexdigest())
        password = salt.hexdigest() + secure_hash.hexdigest()
        # Make sure the hashed password is a unicode object at the end of the
        # process because SQLAlchemy _wants_ unicode objects for Unicode cols
        if not isinstance(password, unicode): 
            password = password.decode('utf-8')
        return password

    def validate_password(self, password):
        """Check the password against existing credentials."""
        secure_hash = sha256()
        if isinstance(password, unicode): 
            password = password.encode('utf-8')
        secure_hash.update(password + str(self.password[:64]))
        return self.password[64:] == secure_hash.hexdigest()

class Group(DeclarativeBase):
    """Group definition."""
    __tablename__ = 'groups'

    # Columns
    id = Column(Integer, primary_key=True) #@ReservedAssignment
    group_name = Column(Unicode(64), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

    # Relations
    users = relationship('User', secondary=user_group_table, backref='groups')

    @classmethod
    def by_group_name(cls, group_name):
        """Return the user object whose group name is ``group_name``."""
        return dbsession.query(cls).filter_by(group_name=group_name).first() #@UndefinedVariable

    # Special methods
    def __repr__(self):
        return ('<Group: %s, display=%s>'%(self.group_name, self.display_name)).encode('utf-8')

    def __unicode__(self):
        return self.display_name or self.group_name

class Permission(DeclarativeBase):
    """Permission definition."""
    __tablename__ = 'permissions'

    # Columns
    id = Column(Integer, primary_key=True) #@ReservedAssignment
    permission_name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(255))

    # Relations
    groups = relationship('Group', secondary=group_permission_table, backref='permissions')

    # Special methods
    def __repr__(self):
        return ('<Permission: name=%s>' % self.permission_name).encode('utf-8')

    def __unicode__(self):
        return self.permission_name