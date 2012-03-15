# -*- coding: utf-8 -*-
"""
fills the database with some startup data.
usage: python -c 'import setup.auth'
"""

from models import dbsession, User, Permission

# User Account
user = User(
    user_name = unicode('admin'),
    display_name = unicode('God'),
    password = unicode('nimda123')
)
dbsession.add(user) #@UndefinedVariable
dbsession.flush() #@UndefinedVariable

permission = Permission(
    permission_name = unicode('admin'),
    user_id = user.id
)

dbsession.add(permission) #@UndefinedVariable
dbsession.flush() #@UndefinedVariable
print 'boot strap complete.'