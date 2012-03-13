# -*- coding: utf-8 -*-
"""
fills the database with some startup data.
usage: python -c 'import setup.auth'
"""

from models import dbsession, Team, User, Box

#Team
team = Team(
              team_name = 'Test Team',
              motto = 'We rock!',
              score = 10
)
dbsession.add(team) #@UndefinedVariable

#Box
box = Box(
            box_name = 'Test',
            ip_address = '192.168.0.1',
            description = 'This is a test box!',
            root_key = "12345",
            user_key = "54321",
            root_value = 500,
            user_value = 100
)

dbsession.add(box) #@UndefinedVariable

# User Account
user = User(
    user_name = 'user',
    display_name = 'cheater',
    dirty = False,
    password = 'user'
)
dbsession.add(user) #@UndefinedVariable
dbsession.flush() #@UndefinedVariable

#Link rows

user.team_id = team.id
dbsession.add(user) #@UndefinedVariable
dbsession.flush() #@UndefinedVariable