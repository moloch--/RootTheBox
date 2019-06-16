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

"""
# pylint: disable=unused-wildcard-import


import os
import sys
import getpass

from libs.ConsoleColors import *
from builtins import str, input
from models import dbsession
from models.Permission import Permission
from models.Theme import Theme, ThemeFile
from models.MarketItem import MarketItem
from models.GameLevel import GameLevel
from models.User import User, ADMIN_PERMISSION
from tornado.options import options


# Fills the database with some startup data.
password = ""

if options.setup.lower().startswith("dev"):
    admin_handle = "admin"
    password = "nimda123"
    print("Admin Username: %s, Password: %s" % (admin_handle, password))
else:
    admin_handle = str(input(PROMPT + "RootTheBox Admin Username [admin]: ")) or "admin"
    sys.stdout.write(PROMPT + "New Admin ")
    sys.stdout.flush()
    password1 = getpass.getpass()
    sys.stdout.write(PROMPT + "Confirm New Admin ")
    sys.stdout.flush()
    password2 = getpass.getpass()
    if password1 == password2 and len(password1) >= options.min_user_password_length:
        password = password1
    else:
        print(
            WARN
            + "Error: Passwords did not match, or was less than %d chars"
            % (options.min_user_password_length,)
        )
        os._exit(1)

# Theme objects
css_files = [
    (u"Bootstrap", [u"bootstrap.min.css"]),
    (u"Amelia", [u"amelia.min.css"]),
    (u"Cyborg", [u"cyborg.min.css"]),
    (u"Readable", [u"readable.min.css"]),
    (u"Slate", [u"slate.min.css"]),
    (u"Spruce", [u"spruce.min.css"]),
    (u"United", [u"united.min.css"]),
    (u"Cerulean", [u"cerulean.min.css"]),
    (u"Journal", [u"journal.min.css"]),
    (u"Simplex", [u"simplex.min.css"]),
    (u"Spacelab", [u"spacelab.min.css"]),
    (u"Superhero", [u"superhero.min.css"]),
    (u"Geocities", [u"geocities.min.css"]),
    (u"386", [u"386.css", u"386.js", u"386.responsive.css"]),
]
for css in css_files:
    theme = Theme(name=css[0])
    dbsession.flush()
    for f in css[1]:
        theme_file = ThemeFile(theme_id=theme.id, file_name=f)
        theme.files.append(theme_file)
        dbsession.add(theme_file)
    dbsession.add(theme)

# Market Items
item = MarketItem(
    name=u"Source Code Market",
    price=500,
    image=u"source_code_market.png",
    description=u"Allows your team access to the Source Code Black Market where you can purchase leaked source code for certain target boxes.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name=u"Password Security",
    price=1000,
    image=u"password_security.png",
    description=u"Allows your team to upgrade their password hashes to more secure algorithms such as SHA1, and SHA256.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name=u"Federal Reserve",
    price=1750,
    image=u"federal_reserve.png",
    description=u"Gain access to the internal New York Federal Reserve banking system, allowing you to transfer funds to/from accounts.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name=u"SWAT",
    price=3000,
    image=u"swat.png",
    description=u"Gain access to the internal police computer system, allowing you to insert fraudlent arrest warrents for other players.",
)
dbsession.add(item)
dbsession.flush()

# Game Levels
game_level = GameLevel(number=0, buyout=0)
dbsession.add(game_level)
dbsession.flush()

# Admin User Account
admin_user = User(handle=admin_handle)
admin_user.password = password
dbsession.add(admin_user)
dbsession.flush()

admin_permission = Permission(name=ADMIN_PERMISSION, user_id=admin_user.id)
dbsession.add(admin_permission)
dbsession.commit()
