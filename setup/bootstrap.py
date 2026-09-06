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


import getpass
import os
import random
import string
import sys
from builtins import input, str

from tornado.options import options

from libs.ConsoleColors import *
from models import dbsession
from models.GameLevel import GameLevel
from models.MarketItem import MarketItem
from models.Permission import Permission
from models.Theme import Theme, ThemeFile
from models.User import ADMIN_PERMISSION, User

# Fills the database with some startup data.
password = ""


def generate_admin_password(length=24):
    """Builds a strong random admin password for unattended (docker) setups"""
    alphabet = string.ascii_letters + string.digits
    return "".join(random.SystemRandom().choice(alphabet) for _ in range(length))


if (
    options.setup.lower().startswith("dev")
    or options.tests
    or options.auth.lower() == "azuread"
):
    admin_handle = "admin"
    password = "rootthebox"
elif options.setup.lower().startswith("docker"):
    admin_handle = os.environ.get("ADMIN_USER", "") or "admin"
    password = os.environ.get("ADMIN_PASSWORD", "")
    if password and len(password) < options.min_user_password_length:
        print(
            WARN
            + "Error: ADMIN_PASSWORD is less than %d chars"
            % (options.min_user_password_length,)
        )
        os._exit(1)
    if not password:
        password = generate_admin_password()
        sys.stdout.write(
            "%sGenerated admin account '%s' with password: %s\n"
            % (INFO, admin_handle, password)
        )
        sys.stdout.write(
            "%sSet ADMIN_PASSWORD to choose it yourself; it is shown only once.\n"
            % (INFO,)
        )
        sys.stdout.flush()
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
    ("Bootstrap", ["bootstrap.min.css"]),
    ("Amelia", ["amelia.min.css"]),
    ("Cyborg", ["cyborg.min.css"]),
    ("Readable", ["readable.min.css"]),
    ("Slate", ["slate.min.css"]),
    ("Spruce", ["spruce.min.css"]),
    ("United", ["united.min.css"]),
    ("Cerulean", ["cerulean.min.css"]),
    ("Journal", ["journal.min.css"]),
    ("Simplex", ["simplex.min.css"]),
    ("Spacelab", ["spacelab.min.css"]),
    ("Superhero", ["superhero.min.css"]),
    ("Geocities", ["geocities.min.css"]),
    ("386", ["386.css", "386.js", "386.responsive.css"]),
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
    name="Source Code Market",
    price=500,
    image="source_code_market.png",
    description="Allows your team access to the Source Code Black Market where you can purchase leaked source code for certain target boxes.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name="Password Security",
    price=1000,
    image="password_security.png",
    description="Allows your team to upgrade their password hashes to more secure algorithms such as SHA1, and SHA256.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name="Federal Reserve",
    price=1750,
    image="federal_reserve.png",
    description="Gain access to the internal New York Federal Reserve banking system, allowing you to transfer funds to/from accounts.",
)
dbsession.add(item)
dbsession.flush()

item = MarketItem(
    name="SWAT",
    price=3000,
    image="swat.png",
    description="Gain access to the internal police computer system, allowing you to insert fraudlent arrest warrents for other players.",
)
dbsession.add(item)
dbsession.flush()

# Game Levels
game_level = GameLevel(number=0, buyout=0)
dbsession.add(game_level)
dbsession.flush()

if options.auth.lower() == "db":
    # Admin User Account
    admin_user = User(handle=admin_handle)
    admin_user.password = password
    dbsession.add(admin_user)
    dbsession.flush()

    admin_permission = Permission(name=ADMIN_PERMISSION, user_id=admin_user.id)
    dbsession.add(admin_permission)

dbsession.commit()
