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

level_0 = GameLevel.all()[0]  # Level 0 is created by the bootstrap

################ [ CREATE YOUR GAME OBJECTS HERE ] ################
# > Create teams
# create_team(TEAM_NAME, TEAM_MOTTO)
team_a = create_team(
    name="The A Team", 
    motto="Pdc Baby"
)

team_b = create_team(
    name="The B Team", 
    motto="Always 2nd Best"
)

# > Create users
# create_user(HACKER_NAME, PASSWORD, BANK_PASSWORD, TEAM_OBJECT)
joe = create_user(
    handle="moloch", 
    password="asdf", 
    bank_password='1234', 
    team=team_a
)
john = create_user(
    handle="hathcox", 
    password="password", 
    bank_password='4321', 
    team=team_a
)

steve = create_user(
    handle="stormcrow", 
    password="qwerty", 
    bank_password='5432', 
    team=team_b
)
rick = create_user(
    handle="wildicv", 
    password="foobar", 
    bank_password='monkey', 
    team=team_b
)

# > Create game levels
# create_game_level(LEVEL_NUMBER, BUYOUT)
level_1 = create_game_level(
    number=1, 
    buyout=5000
)
level_2 = create_game_level(
    number=2, 
    buyout=7500
)

# > Create Corporations
# create_corporation(CORP_NAME, CORP_DESCRIPTION)
seatec = create_corporation(
    name="SEATEC Astronomy", 
    description="No more secrets"
)
microshaft = create_corporation(
    name="Micro$haft", 
    description="All we want, is your money"
)

# > Crate Boxes
# create_box(BOX_NAME, CORP_OBJECT, DIFFICUTLY, LEVEL_OBJECT, DESCRIPTION, LIST_OF_IPv4, LIST_OF_IPv6)
seatec_mail = create_box(
    name="Mail Server", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Your employer requests that you locate several items on this server.  " +\
            "Intel reports its a UNIX server located somewhere in 192.168.2.20-100",
    ipv4_addresses=["192.168.2.50"]
)
seatec_fw = create_box(
    name="Firewall", 
    corporation=seatec, 
    difficulty="Hard", 
    game_level=level_0, 
    description="",
    ipv4_addresses=["192.168.2.1"]
)
microshaft_web = create_box(
    name="Web Server", 
    corporation=microshaft, 
    difficulty="Medium", 
    game_level=level_1, 
    description="",
    ipv4_addresses=["192.168.3.2"]
)
microshaft_dev = create_box(
    name="Stage Server", 
    corporation=microshaft, 
    difficulty="Medium", 
    game_level=level_1, 
    description="",
    ipv4_addresses=["192.168.3.4"]
)
microshaft_laptop = create_box(
    name="CEO Laptop", 
    corporation=microshaft, 
    difficulty="Hard", 
    game_level=level_2, 
    description="",
    ipv4_addresses=["127.0.0.1"]
)

# > Create Flags
# create_flag(FLAG_NAME, TOKEN, REWARD_VALUE, BOX_OBJECT, DESCRIPTION, IS_FILE)
# IS_FILE: The flag is a file (and TOKEN should be the local path to the file)
create_flag(
    name="DB Access", 
    token="p@ssw0rd", 
    value=1000, 
    box=seatec_mail, 
    description="Get the MySQL root password for the mail server"
)

create_flag(
    name="Guess this", 
    token="toor", 
    value=1500, 
    box=seatec_mail, 
    description="Get the root password for the mail server"
)

create_flag(
    name="Tro.py", 
    token="./rootthebox.py", 
    value=2500, 
    box=seatec_fw, 
    description="Get the source code for rootthebox.py", 
    is_file=True
)

create_flag(
    name="One Key to Rule Them All", 
    token="kfahjl*&y63hja", 
    value=5000, 
    box=microshaft_web, 
    description="Obtain Micro$haft's Amazon Cloud Private Key"
)

create_flag(
    name="Call me maybe", 
    token="867-5309", 
    value=1500, 
    box=microshaft_laptop, 
    description="Find the Micro$shaft CEO's home phone number"
)

# > Create Hints
# create_hint(BOX, PRICE, DESCRIPTION)
create_hint(
    box=seatec_fw, 
    price=1000, 
    description="Look for interesting HTTP headers."
)

