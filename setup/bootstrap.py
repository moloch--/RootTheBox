# -*- coding: utf-8 -*-
"""
    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

-------

fills the database with some startup data.
usage: python -c 'import setup.auth'

"""


import os
import sys
import getpass

from libs.ConsoleColors import *
from libs.ConfigManager import ConfigManager
from models import dbsession, User, Permission, Theme, \
                    MarketItem, GameLevel, GameSettings


# Fills the database with some startup data.
config = ConfigManager.Instance()
password = ""

if config.debug:
    password = 'nimda123'
else:
    sys.stdout.write(PROMPT + "New Admin ")
    sys.stdout.flush()
    password1 = getpass.getpass()
    sys.stdout.write(PROMPT + "Confirm New Admin ")
    sys.stdout.flush()
    password2 = getpass.getpass()
    if password1 == password2 and 12 <= len(password1):
        password = password1
    else:
        print WARN + \
            'Error: Passwords did not match, or were less than 12 chars'
        os._exit(1)

# Theme objects
css_files = [
    (u"Bootstrap", u'bootstrap.min.css'),
    (u"Amelia", u'amelia.min.css'),
    (u"Cyborg", u'cyborg.min.css'),
    (u"Readable", u'readable.min.css'),
    (u"Slate", u'slate.min.css'),
    (u"Spruce", u'spruce.min.css'),
    (u"United", u'united.min.css'),
    (u"Cerulean", u'cerulean.min.css'),
    (u"Journal", u'journal.min.css'),
    (u"Simplex", u'simplex.min.css'),
    (u"Spacelab", u'spacelab.min.css'),
    (u"Superhero", u'superhero.min.css'),
]
for css in css_files:
    theme = Theme(
        name=css[0],
        cssfile=css[1],
    )
    dbsession.add(theme)
    dbsession.flush()

# Market Items
item = MarketItem(
    name=u"Source Code Market",
    price=5000,
    description=u"Buy leaked source code.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name=u"Password Security",
    price=7500,
    description=u"Allows your team to upgrade their password hashes to SHA1, and SHA256.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name=u"Federal Reserve",
    price=10000,
    description=u"Gain access to the internal New York Federal Reserve banking system, allowing you to transfer funds to/from accounts.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name=u"SWAT",
    price=100000,
    description=u"Gain access to the internal police computer system, allowing you to insert fraudlent arrest warrents for other players.",
)
dbsession.add(item)
dbsession.flush()

# Game Levels
game_level = GameLevel(
    number=0,
    buyout=0,
)
dbsession.add(game_level)
dbsession.flush()

# Admin User Account
user = User(
    account=u'admin',
    handle=u'God',
    algorithm=u'pbkdf2',
)
dbsession.add(user)
dbsession.flush()
user.password = password
dbsession.add(user)
dbsession.flush()

permission = Permission(
    name=u'admin',
    user_id=user.id
)
dbsession.add(permission)
dbsession.flush()

# Create intital game settings
game_settings = GameSettings()
game_settings.is_active = True
dbsession.add(game_settings)
dbsession.flush()

# Display Details
if config.debug:
    environ = bold + R + "Developement boot strap" + W
    details = ", default admin password is '%s'." % password
else:
    environ = bold + "Production boot strap" + W
    details = '.'
print INFO + '%s completed successfully%s' % (environ, details)
