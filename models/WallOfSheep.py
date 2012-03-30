'''
Created on Mar 21, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Integer, Unicode
from models import dbsession, User
from models.BaseGameObject import BaseObject

class WallOfSheep(BaseObject):

    preimage = Column(Unicode(64), nullable=False)
    point_value = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    cracker_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    @property
    def user(self):
        ''' Returns display name of user'''
        return User.by_user_id(self.user_id)
   
    @property
    def cracker(self):
        ''' Returns display name of cracker '''
        return User.by_user_id(self.cracker_id)

    @classmethod
    def get_all(cls):
        ''' Returns all team objects '''
        return dbsession.query(cls).order_by(desc(cls.created)).all()

    @classmethod
    def by_user_id(cls, user_id):
        ''' Returns all entries for a user_id '''
        return dbsession.query(cls).filter_by(user_id=user_id).all()

    @classmethod
    def by_cracker_id(cls, cracker_id):
        ''' Returns all entries for cracker_id '''
        return dbsession.query(cls).filter_by(cracker_id=cracker_id).all()

    def __repr__(self):
        return ('<WallOfSheep - preimage: %s, user_id: %d>' % (self.preimage, self.user_id)).encode('utf-8')
