# -*- coding: utf-8 -*-
"""
fills the database with some startup data.
usage: python -c 'import setup.auth'
"""

from models import dbsession, Group, Permission, User

# Groups and Permissions
g_admins = Group(
    group_name = 'admins',
    display_name = 'the administrators of the application'
)
dbsession.add(g_admins) #@UndefinedVariable

p_admin = Permission(
    permission_name = 'admin',
    description = 'an administrator permission, allows everything'
)
p_admin.groups.append(g_admins)
dbsession.add(p_admin) #@UndefinedVariable

# Admin Account
u_admin = User(
    user_name = 'admin',
    display_name = 'the administrator',
    email_address = 'admin@admin.com',
    password = 'admin'
)
dbsession.add(u_admin) #@UndefinedVariable
g_admins.users.append(u_admin)

# User Account
u_user = User(
    user_name = 'user',
    display_name = 'a simple user',
    email_address = 'user@user.com',
    password = 'user'
)
dbsession.add(u_user) #@UndefinedVariable

dbsession.flush() #@UndefinedVariable