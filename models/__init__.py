# -*- coding: utf-8 -*-
"""
this sets up sqlalchemy.
for more information about sqlalchemy check out <a href="http://www.sqlalchemy.org/">www.sqlalchemy.org</a>
"""

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Integer
from sqlalchemy.orm import sessionmaker
from models.BaseGameObject import BaseObject

metadata = BaseObject.metadata

# set the connection string here
engine = create_engine('mysql://rtbUser:rtbUser@localhost/rtb')
Session = sessionmaker(bind=engine, autocommit=True)

# import the dbsession instance to execute queries on your database
dbsession = Session(autoflush = True)

association_table = Table('user_to_box', BaseObject.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('box_id', Integer, ForeignKey('box.id'), nullable=False)
)

team_challenges = Table('team_to_challenge', BaseObject.metadata,
    Column('team_id', Integer, ForeignKey('team.id'), nullable=False),
    Column('challenge_id', Integer, ForeignKey('challenge.id'), nullable=False)
)

# import models.
from models.Action import Action
from models.Box import Box
from models.Post import Post
from models.CrackMe import CrackMe
from models.Permission import Permission
from models.Team import Team
from models.User import User
from models.FileUpload import FileUpload
from models.Challenge import Challenge
from models.WallOfSheep import WallOfSheep

# calling this will create the tables at the database
__create__ = lambda: (setattr(engine, 'echo', True), metadata.create_all(engine))

# Bootstrap the database with some shit
def __boot_strap__() :
    import setup.auth
    
    
    
    
