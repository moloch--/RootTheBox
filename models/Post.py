'''
Created on Mar 12, 2012

@author: moloch
'''

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject

class Post(BaseObject):
    ''' Post definition '''
    
    name = Column(Unicode(255), nullable=False)
    contents = Column(Unicode(1024), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return ('<Post - name:%s, user_id:%d>' % (self.name, self.user_id))
    



