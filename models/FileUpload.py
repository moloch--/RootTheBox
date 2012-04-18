'''
Created on Mar 15, 2012

@author: moloch

 Copyright [2012] [Redacted Labs]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from models import dbsession
from sqlalchemy.types import Unicode, Integer
from sqlalchemy import Column, ForeignKey
from models.BaseGameObject import BaseObject

class FileUpload(BaseObject):
    
    file_name = Column(Unicode(255), nullable=False)
    content = Column(Unicode(255))
    uuid = Column(Unicode(64), unique=True, nullable=False)
    description = Column(Unicode(1024))
    byte_size = Column(Integer)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)

    @classmethod
    def by_uuid(cls, uuid):
        """ Return the user object whose uuid is ``uuid`` """
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()
        
    @classmethod
    def by_file_name(cls, file_name):
        """ Return the user object whose file name is ``file_name`` """
        return dbsession.query(cls).filter_by(file_name=unicode(file_name)).first()
    
    def __repr__(self):
        return ('<File - name: %s, type: %s>' % (self.file_name, self.content))

