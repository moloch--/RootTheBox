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

This file lets you script the game setup; if you're not familair with
Python I recommend using the WebUI to setup the game as it takes care of all
the details for you.

'''

from setup.helpers import *
from libs.ConsoleColors import *

level_0 = GameLevel.all()[0]  # Level 0 is created by the bootstrap

################ [ CREATE YOUR GAME OBJECTS HERE ] ################
# Create teams
# create_team(TEAM_NAME, TEAM_MOTTO)
team_a = create_team("The A Team", "Pdc Baby")
team_b = create_team("The B Team", "Always 2nd Best")

# Create users
# create_user(ACCOUNT_NAME, HACKER_NAME, PASSWORD, TEAM_OBJECT)
joe = create_user("joe", "moloch", "asdf", team_a)
john = create_user("john", "hathcox", "password", team_a)

steve = create_user("steve", "stormcrow", "qwerty", team_b)
rick = create_user("rick", "wildicv", "foobar", team_b)

# Create game levels
# create_game_level(LEVEL_NUMBER, BUYOUT)
level_1 = create_game_level(1, 5000)
level_2 = create_game_level(2, 7500)

# Create Corporations
# create_corporation(CORP_NAME, CORP_DESCRIPTION)
seatec = create_corporation("SEATEC Astronomy", "No more secrets")
microshaft = create_corporation("Micro$haft", "All we want, is your money")

# Crate Boxes
# create_box(BOX_NAME, CORP_OBJECT, DIFFICUTLY, LEVEL_OBJECT, LIST_OF_IPv4, LIST_OF_IPv6)
seatec_mail = create_box("Mail Server", seatec, "Easy", level_0, ipv4_addresses=["192.168.2.50"])
seatec_fw = create_box("Firewall", seatec, "Hard", level_0, ipv4_addresses=["192.168.2.1"])

microshaft_web = create_box("Web Server", microshaft, "Medium", level_1, ipv4_addresses=["192.168.3.2"])
microshaft_dev = create_box("Stage Server", microshaft, "Medium", level_1, ipv4_addresses=["192.168.3.4"])
microshaft_laptop = create_box("CEO Laptop", microshaft, "Hard", level_2, ipv4_addresses=["192.168.3.25"])

# Create Flags
# create_flag(FLAG_NAME, TOKEN, REWARD_VALUE, BOX_OBJECT, DESCRIPTION, IS_FILE, IS_REGEX, IS_HASH)
# IS_FILE: The user should submit a file, the token is the md5 of the file
# IS_REGEX: The user should submit a string, the token is a regex if the string matches the flag submission is successful
# IS_HASH:  The user's submissions should be hashed with md5 before getting compared to the stored token
create_flag("DB Access", "p@ssw0rd", 1000, seatec_mail, "Get the MySQL root password for the mail server")
create_flag("Guess this", "toor", 1500, seatec_mail, "Get the root password for the mail server")
create_flag("Troy", "lulwat", 2500, seatec_fw, "Get the password for the SEATEC firewall administrator")

create_flag("One Key to Rule Them All", "kfahjl*&y63hja", 5000, microshaft_web, "Obtain Micro$haft's Amazon Cloud Private Key")
create_flag("DMZ", "d08fd5b639c512f852f6a1696efba49a", 3500, microshaft_dev, "Obtain a .tar ball of Micro$haft's Winblowz source code", is_file=True)
create_flag("Call me maybe", "867-5309", 1500, microshaft_laptop, "Find the Micro$shaft CEO's home phone number")

