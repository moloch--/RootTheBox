# -*- coding: utf-8 -*-
"""
fills the database with some startup data.
usage: python -c 'import setup.auth'
"""
import os
import sys
import getpass

from models import dbsession, User, Permission

DEV_ENVIRON = False

if DEV_ENVIRON:
	password = 'nimda123'
else:
	sys.stdout.write("[?] New Admin ")
	sys.stdout.flush()
	password1 = getpass.getpass()
	sys.stdout.write("[?] Confirm New Admin ")
	sys.stdout.flush()
	password2 = getpass.getpass()
	if password1 == password2 and 8 < len(password1):
		password = password1
	else:
		print '[!] Error: Passwords did not match, or were too short'
		os._exit(1)

# User Account
user = User(
    user_name = unicode('admin'),
    display_name = unicode('God'),
    password = unicode(password)
)
dbsession.add(user)
dbsession.flush()

permission = Permission(
    permission_name = unicode('admin'),
    user_id = user.id
)

dbsession.add(permission)
dbsession.flush()
print 'boot strap complete.'
