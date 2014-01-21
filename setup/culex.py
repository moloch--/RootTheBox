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
buffaloes = create_team(
    name="The Great White Buffalo", 
    motto="Don't let it get away!"
)

violators = create_team(
    name="The Violators", 
    motto="Always invest!"
)

# > Create users
# create_user(HACKER_NAME, PASSWORD, BANK_PASSWORD, TEAM_OBJECT)
'''
joe = create_user(
    handle="moloch", 
    password="asdf", 
    bank_password='1234', 
    team=buffaloes
)
'''
# > Create game levels
# create_game_level(LEVEL_NUMBER, BUYOUT)
'''
level_1 = create_game_level(
    number=1, 
    buyout=5000
)
level_2 = create_game_level(
    number=2, 
    buyout=7500
)
'''
# > Create Corporations
# create_corporation(CORP_NAME, CORP_DESCRIPTION)
seatec = create_corporation(
    name="SEATEC Astronomy", 
    description="No more secrets"
)

lougle = create_corporation(
    name="Lougle", 
    description="All your knowledge"
)

# > Crate Boxes
# create_box(BOX_NAME, CORP_OBJECT, DIFFICUTLY, LEVEL_OBJECT, 
#            DESCRIPTION, GARBAGE, LIST_OF_IPv4, LIST_OF_IPv6, AVATAR)
seatec_walsh = create_box(
    name="Walsh", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0,
    description="Your employer requests that you locate several items on this system.  " +\
            "Intel reports it to be a Windows system located somewhere in 192.168.x.10-100",
    ipv4_addresses=["192.168.3.16"],
    ipv4_addresses=["192.168.5.16"],
    avatar="cmd_prompt.jpg"
)

seatec_kluwe = create_box(
    name="Kluwe", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="This system is also a product of the Microsoft Corporation and found the the 192.168.x.10-100 range.",
    ipv4_addresses=["192.168.3.15"],
    ipv4_addresses=["192.168.5.15"],
    avatar="trinity.jpg"
)

seatec_rudolph = create_box(
    name="Rudolph", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Evil Worker System",
    ipv4_addresses=["192.168.3.61"],
    ipv4_addresses=["192.168.5.61"],
    avatar="bad_chip.jpg"
)

seatec_wright = create_box(
    name="Wright", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Evil Worker System Two",
    ipv4_addresses=["192.168.3.57"],
    ipv4_addresses=["192.168.5.57"],
    avatar="images.jpg"
)

seatec_peterson = create_box(
    name="Peterson", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Evil Worker System Three",
    ipv4_addresses=["192.168.3.8"],
    ipv4_addresses=["192.168.5.8"],
    avatar="lovetheinternet.jpg"
)

seatec_gerhart = create_box(
    name="Gerhart", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Security Department Worker System",
    ipv4_addresses=["192.168.3.92"],
    ipv4_addresses=["192.168.5.92"],
    ipv4_addresses=["192.168.123.1"],
    ipv4_addresses=["192.168.125.1"],
    avatar="backdoor_win.jpg"
)

seatec_gerhart2 = create_box(
    name="Gerhart2", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Security Department Internal System",
    ipv4_addresses=["192.168.123.5"],
    ipv4_addresses=["192.168.125.5"],
    ipv4_addresses=["192.168.223.3"],
    ipv4_addresses=["192.168.225.3"],
    avatar="firewall.jpg"
)

seatec_gerhart3 = create_box(
    name="Gerhart3", 
    corporation=seatec, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Security Department Internal System Two",
    ipv4_addresses=["192.168.223.7"],
    ipv4_addresses=["192.168.225.7"],
    avatar="download.jpg"
)

lougle_allen = create_box(
    name="Allen", 
    corporation=lougle, 
    difficulty="Easy", 
    game_level=level_0, 
    description="HR Department Workstation",
    ipv4_addresses=["192.168.3.9"],
    ipv4_addresses=["192.168.5.9"],
    avatar="download.jpg"
)

lougle_webb = create_box(
    name="Webb", 
    corporation=lougle, 
    difficulty="Easy", 
    game_level=level_0, 
    description="HR Department Workstation Two",
    ipv4_addresses=["192.168.3.40"],
    ipv4_addresses=["192.168.5.40"],
    avatar="lougle.jpg"
)

lougle_carter = create_box(
    name="Carter", 
    corporation=lougle, 
    difficulty="Easy", 
    game_level=level_0, 
    description="HR Department Chief Workstation",
    ipv4_addresses=["192.168.3.40"],
    ipv4_addresses=["192.168.5.40"],
    avatar="php_code.jpg"
)

lougle_williams = create_box(
    name="Williams", 
    corporation=lougle, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Security Department Chief Workstation",
    ipv4_addresses=["192.168.3.43"],
    ipv4_addresses=["192.168.5.43"],
    avatar="the-code.jpg"
)

lougle_kaspersky = create_box(
    name="kaspersky", 
    corporation=lougle, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Accounting Department Workstation",
    ipv4_addresses=["192.168.3.17"],
    ipv4_addresses=["192.168.5.17"],
    avatar="warning.jpg"
)

lougle_kalil = create_box(
    name="Kalil", 
    corporation=lougle, 
    difficulty="Easy", 
    game_level=level_0, 
    description="Accounting Department Workstation Two",
    ipv4_addresses=["192.168.3.129"],
    ipv4_addresses=["192.168.5.129"],
    avatar="world.jpg"
)

# > Create Flags
# create_flag(FLAG_NAME, TOKEN, REWARD_VALUE, BOX_OBJECT, DESCRIPTION, IS_FILE)
# IS_FILE: The flag is a file (and TOKEN should be the local path to the file)

create_flag(
    name="PCAP",
    token="ms10_061_spoolss", 
    value=1000, 
    box=seatec_walsh, 
    description="Identify the module name of the exploit used in the PCAP file. (lower_case)"
)

create_flag(
    name="Common",
    token="Baltimore Ravens", 
    value=1000, 
    box=seatec_walsh, 
    description="Identify the second command run on the target. (Two Names)"
)

create_flag(
    name="Copied",
    token="flag2.exe", 
    value=1000, 
    box=seatec_walsh, 
    description="Identify that a file was copied to the target. (lower-case)"
)

create_flag(
    name="runcmd",
    token="Atlanta Falcons", 
    value=1000, 
    box=seatec_walsh, 
    description="Carve out the executable from FLAG.pcap and view it in a hex editor. (Two Names)"
)

create_flag(
    name="write_snort",
    token="Washington Redskins", 
    value=1000, 
    box=seatec_walsh, 
    description="Write a Snort signature to catch the exploit run against printers, exploit must be logged. (Instructor)"
)

create_flag(
    name="Scheduled", 
    token="tampabaybucs.exe", 
    value=1500, 
    box=seatec_kluwe, 
    description="What is the name of the program scheduled to run? (lower-case)"
)

create_flag(
    name="Scheduled", 
    token="SAINTS", 
    value=1500, 
    box=seatec_kluwe, 
    description="Find the codeword in FLAG.pcap. (all-caps)"
)

create_flag(
    name="Exploit Thrown", 
    token="ms08_067_netapi", 
    value=1500, 
    box=seatec_rudolph, 
    description="Identify exploit thrown at target in FLAG.pcap. (lower_case)"
)

create_flag(
    name="Commands Run", 
    token="Philly Eagles!!!", 
    value=1500, 
    box=seatec_rudolph, 
    description="Identify commands run on target shell, not meterpreter. (Two Names)"
)

create_flag(
    name="Files Uploaded", 
    token="SanDiegoChargers!!!",
    value=1500, 
    box=seatec_rudolph, 
    description="Identify if anything was uploaded to the target. (One Name)"
)

create_flag(
    name="Snort Signature", 
    token="Seattle Seahawks",
    value=1500, 
    box=seatec_rudolph, 
    description="Write a successful Snort Sig for exploit run on target and have it log. (Instructor)"
)

create_flag(
    name="Files Uploaded", 
    token="Houston Texans",
    value=1500, 
    box=seatec_rudolph, 
    description="Run string on the file that was uploaded to the target. (Two Names)"
)

create_flag(
    name="Recently Run", 
    token="Browns.exe",
    value=1500, 
    box=seatec_wright, 
    description="What application recently run stands out? (One Name)"
)

create_flag(
    name="Something Running", 
    token="Denver Broncos",
    value=1500, 
    box=seatec_wright, 
    description="Something running to lure people in. Check out their desktop. (Two Names)"
)

create_flag(
    name="Implant Me", 
    token="Buffalo Bills",
    value=1500, 
    box=seatec_peterson, 
    description="Implant target with METSVC and get back on. (Instructor)"
)

create_flag(
    name="DLL Hook", 
    token="appinit_dlls",
    value=1500, 
    box=seatec_peterson, 
    description="Investigate where malware might be loaded by user32.dll. (lower-case)"
)

create_flag(
    name="Thumbdrives", 
    token="03:34",
    value=1500, 
    box=seatec_gerhart, 
    description="Somebody's been plugging thumbdrives in. Find the last write time to that thumbdrive. (HH:MM)"
)

create_flag(
    name="Odd Software", 
    token="Da_Bears.exe",
    value=1500, 
    box=seatec_gerhart, 
    description="Find any odd software in the registry. (One Name, *.exe)"
)

create_flag(
    name="Odd Firewall Rule", 
    token="St Louis Rams",
    value=1500, 
    box=lougle_allen, 
    description="Find any odd firewall rule in the registry. (Three Names)"
)

create_flag(
    name="Soon to be Renamed", 
    token="STEELERS.exe",
    value=1500, 
    box=lougle_allen, 
    description="Find in the registry the file which is about to be modified. (*.exe all-caps)"
)

create_flag(
    name="Random Request", 
    token="Miami Dolphins",
    value=1500, 
    box=lougle_webb, 
    description="Embed calc.exe with a payload for Webb and notify instructor. (Instructor)"
)

create_flag(
    name="URL Retrieval", 
    token="greenbaypackers",
    value=1500, 
    box=lougle_carter, 
    description="Identify source of client side exploit. (lower-case)"
)
'''
create_flag(
    name="Exploit Used", 
    token="JacksonvilleJaguars",
    value=1500, 
    box=lougle_carter, 
    description="Find the exploit used on target. (One Name)"
)
'''
create_flag(
    name="On Boot", 
    token="Indianapolis Colts",
    value=1500, 
    box=lougle_carter, 
    description="Identify malicious executable which will start on boot. (Two Names)"
)

create_flag(
    name="Firewall Rule", 
    token="49ers",
    value=1500, 
    box=lougle_carter, 
    description="Open a firewall rule that allows connections to .exe (Instructor)"
)

create_flag(
    name="Evidence Quest", 
    token="KansasCityChiefs",
    value=1500, 
    box=lougle_williams, 
    description="Dump the domain admin credentials. (Instructor)"
)

create_flag(
    name="Deleted Docs", 
    token="raiders",
    value=1500, 
    box=lougle_kaspersky, 
    description="Find the document recently deleted, what did it say? (One Name)"
)

create_flag(
    name="Cleanup Task", 
    token="NewEnglandPatriots",
    value=1500, 
    box=lougle_kaspersky, 
    description="Prevent others from gaining access the way you did. (Instructor)"
)

create_flag(
    name="Cleanup Task", 
    token="Giants",
    value=1500, 
    box=lougle_kalil, 
    description="Prevent others from gaining access the way you did. (Instructor)"
)

create_flag(
    name="Easter Egg One", 
    token="DallasCowboys",
    value=1500, 
    box=seatec_gerhart2, 
    description="Get into this box. (Instructor)"
)

create_flag(
    name="Easter Egg Two", 
    token="MinnesotaVikings",
    value=1500, 
    box=seatec_gerhart3, 
    description="Get into this box. (Instructor)"
)


# > Create Hints
# create_hint(BOX, PRICE, DESCRIPTION)
create_hint(
    box=seatec_gerhart2, 
    price=5000, 
    description="Interface with the .92 box and address the situation..." 
)

create_hint(
    box=seatec_gerhart3, 
    price=5000, 
    description="Don't let your callback get burned in the great wall of fire..."
)

