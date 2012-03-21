'''
Created on Mar 12, 2012

@author: moloch
'''

from hashlib import md5, sha256
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession, association_table
from models.Box import Box
from models.Team import Team
from models.Post import Post
from models.Action import Action
from models.Permission import Permission
from models.BaseGameObject import BaseObject


class User(BaseObject):
    """ User definition """

    user_name = Column(Unicode(64), unique=True, nullable=False)
    display_name = Column(Unicode(64), unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey('team.id'))
    dirty = Column(Boolean, default=True)
    score_cache = Column(Integer, default=0)
    actions = relationship("Action", backref=backref("User", lazy="joined"), cascade="all, delete-orphan")
    posts = relationship("Post", backref=backref("User", lazy="joined"), cascade="all, delete-orphan")
    permissions = relationship("Permission", backref=backref("User", lazy="joined"), cascade="all, delete-orphan")
    avatar = Column(Unicode(64), default=unicode("default_avatar.gif"))
    controlled_boxes = relationship("Box", secondary=association_table, backref="User")

    _password = Column('password', Unicode(128))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password', self.__class__._hash_password(password))
    ))
    
    def __repr__(self):
        return ('<User - name: %s, display: %s, team_id: %d>' % (self.user_name, self.display_name, self.team_id)).encode('utf-8')

    def __radd__(self, other):
        return self.score + other

    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        return dbsession.query(Permission).filter_by(user_id=self.id) #@UndefinedVariable

    @property
    def permissions_names(self):
        """Return a list with all permissions names granted to the user."""
        return [p.permission_name for p in self.permissions]
        
    @property
    def team_name(self):
        """ Return a list with all groups names the user is a member of """
        if self.team_id == None:
            return None
        else:
            team = dbsession.query(Team).filter_by(id=self.team_id).first() #@UndefinedVariable
            return team.team_name
    
    @property
    def team(self):
        """ Return a the uesr's team object """
        if self.team_id == None:
            return None
        else:
            return dbsession.query(Team).filter_by(id=self.team_id).first() #@UndefinedVariable
    
    @property
    def score(self):
        ''' Returns user's current score from cache, or re-calculates if expired '''
        if self.dirty:
            actions = dbsession.query(Action).filter_by(user_id=self.id).all() #@UndefinedVariable
            self.score_cache = sum(actions)
            self.dirty = False
            dbsession.add(self)
        return self.score_cache
    
    @classmethod
    def get_all(cls):
        """ Return all non-admin user objects """
        return dbsession.query(cls).filter(cls.user_name != 'admin').all() #@UndefinedVariable
    
    @classmethod
    def get_free_agents(cls):
        """ Return all non-admin user objects without a team """
        return dbsession.query(cls).filter_by(team_id=None).filter(cls.user_name != 'admin').all() #@UndefinedVariable
    
    @classmethod
    def by_user_name(cls, user_name):
        """ Return the user object whose user name is ``user_name`` """
        return dbsession.query(cls).filter_by(user_name=unicode(user_name)).first() #@UndefinedVariable
    
    @classmethod
    def by_display_name(cls, display_name):
        """ Return the user object whose user name is ``display_name`` """
        return dbsession.query(cls).filter_by(display_name=unicode(display_name)).first() #@UndefinedVariable
    
    @classmethod
    def by_user_id(cls, user_id):
        """ Return the user object whose user id is ``user_id`` """
        return dbsession.query(cls).filter_by(id=user_id).first() #@UndefinedVariable

    @classmethod
    def add_to_team(cls, team_name):
        ''' Add user to team based on team name '''
        team = dbsession.query(Team).filter_by(team_name=unicode(team_name)).first() #@UndefinedVariable
        cls.team_id = team.id
    
    @classmethod
    def _hash_password(cls, password):
        ''' Hashes the password using Md5/Sha256 :D '''
        if isinstance(password, unicode): 
            password = password.encode('utf-8')
        if 8 <= len(password):
            password = cls.adminHash(password)
        else:
            password = cls.userHash(password)
        return password

    @classmethod
    def userHash(cls, preimage):
        ''' Single round md5 '''
        md5Hash = md5()
        md5Hash.update(preimage)
        return unicode(md5Hash.hexdigest())
    
    @classmethod
    def adminHash(cls, preimage):
        ''' Two rounds of sha256, with a static non-ascii salt because I'm lazy '''
        shaHash = sha256()
        shaHash.update(preimage)
        shaHash.update(preimage + shaHash.hexdigest() + "\x90\x90\x90")
        return unicode(shaHash.hexdigest())
    
    def has_permission(self, permission):
        """ Return True if ``permission`` is in permissions_names """
        return True if permission in self.permissions_names else False

    def validate_password(self, attempt):
        """ Check the password against existing credentials """
        if isinstance(attempt, unicode):
            attempt = attempt.encode('utf-8')
        if self.has_permission('admin'):
            return self.password == self.adminHash(attempt)
        else:
            return self.password == self.userHash(unicode(attempt))
    
    def give_control(self, box_name):
        ''' Give team control of a box object '''
        box = Box.by_box_name(unicode(box_name))
        if not self.is_controlling(box.box_name):
            self.controlled_boxes.append(box)
    
    def lost_control(self, box_name):
        ''' Remove team's control over a box object '''
        if self.is_controlling(Box.by_box_name(box_name)):
            self.controlled_boxes.remove(Box.by_box_name(box_name))
