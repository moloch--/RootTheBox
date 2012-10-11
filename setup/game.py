# -*- coding: utf-8 -*-
'''
Created on Oct 10, 2012

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
------------------------------------------------------------------------------

                !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                ! This file is for advanced users only !
                !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

This file lets you script the game setup; if you're not familair with
Python I recommend using the WebUI to setup the game as it takes care of all
the details for you.  Remember to use unicode strings to avoid type warnings.

'''

from models import dbsession, GameLevel, Flag, Box, Corporation, User, Team

level_0 = GameLevel.all()[0] # Level 0 is created by the bootstrap

# Create teams
team_a = Team(
    name=u"The A Team",
    motto=u"Pdc",
)
team_a.game_levels.append(level_0)
dbsession.add(team_a)
dbsession.flush()

team_b = Team(
    name=u"The B Team",
    motto=u"Always 2nd Best",
)
team_b.game_levels.append(level_0)
dbsession.add(team_b)
dbsession.flush()

# Create users
user = User(
    account=u"joe",
    handle=u"moloch",
    team_id=team_a.id,
)
dbsession.add(user)
dbsession.flush()
user.password = "asdf"
dbsession.add(user)
dbsession.flush()

user = User(
    account=u"haxor",
    handle=u"l33t",
    team_id=team_b.id,
)
dbsession.add(user)
dbsession.flush()
user.password = "asdf"
dbsession.add(user)
dbsession.flush()

# Create corps
seatec = Corporation(
    name=u"SEATEC Astronomy",
    description=u"No More Secrets",
)
dbsession.add(seatec)
dbsession.flush()

# Create boxes
box = Box(
    name=u"Rhea",
    corporation_id=seatec.id,
    difficulty=u"Easy",
    game_level_id=level_0.id,
)
dbsession.add(box)
dbsession.flush()

box = Box(
    name=u"Titan",
    corporation_id=seatec.id,
    difficulty=u"Medium",
    game_level_id=level_0.id,
)
dbsession.add(box)
dbsession.flush()