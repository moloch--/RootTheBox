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
the details for you.

'''

from setup.helpers import *
from libs.ConsoleColors import *
from models import dbsession, GameLevel, IpAddress, Flag, Box, Corporation, User, Team

level_0 = GameLevel.all()[0] # Level 0 is created by the bootstrap

################ [ CREATE YOUR GAME OBJECTS HERE ] ################

team_a = create_team("The A Team", "Pdc Baby")
team_b = create_team("The B Team", "Always 2nd Best")

joe = create_user("joe", "moloch", "asdf", team_a)
john = create_user("john", "hathcox", "password", team_a)

steve = create_user("steve", "stormcrow", "qwerty", team_b)
rick = create_user("rick", "wildicv", "foobar", team_b)

level_1 = create_game_level(1, 5000)
level_2 = create_game_level(2, 7500)

seatec = create_corporation("SEATEC Astronomy", "No more secrets")
microshaft = create_corporation("Micro$haft", "All we want, is your money")

seatec_mail = create_box("Mail Server", seatec, "Easy", level_0, ipv4_addresses=["192.168.2.50"])
seatec_fw = create_box("Firewall", seatec, "Hard", level_0, ipv4_addresses=["192.168.2.1"])

microshaft_web = create_box("Web Server", microshaft, "Medium", level_1, ipv4_addresses=["192.168.3.2"])
microshaft_dev = create_box("Stage Server", microshaft, "Medium", level_1, ipv4_addresses=["192.168.3.4"])
microshaft_laptop = create_box("CEO Laptop", microshaft, "Hard", level_2, ipv4_addresses=["192.168.3.25"])
