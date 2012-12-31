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
'''

from libs.ConsoleColors import *
from models import dbsession, GameLevel, IpAddress, \
    Flag, Box, Corporation, User, Team


def create_game_level(level_number, buyout):
    print(INFO + "Create game level " + bold + "#" + str(level_number) + W + \
        " with a buyout of " + bold + "$" + str(buyout) + W)
    new_level = GameLevel(
        number=level_number,
        buyout=buyout,
    )
    game_levels = GameLevel.all()
    game_levels.append(new_level)
    print(INFO + "Updating game level linked list ...")
    game_levels = sorted(game_levels)
    index = 0
    for level in game_levels[:-1]:
        level.next_level_id = game_levels[index + 1].id
        dbsession.add(level)
        index += 1
    game_levels[0].number = 0
    dbsession.add(game_levels[0])
    game_levels[-1].next_level_id = None
    dbsession.add(game_levels[-1])
    dbsession.flush()
    return new_level


def create_team(name, motto):
    print(INFO + "Create team: " + bold + name + W)
    team = Team(
        name=unicode(name),
        motto=unicode(motto),
    )
    level_0 = GameLevel.all()[0]
    team.game_levels.append(level_0)
    dbsession.add(team)
    dbsession.flush()
    return team


def create_user(account, handle, password, team):
    print(INFO + "Create user: " + bold + account + W)
    user = User(
        account=unicode(account),
        handle=unicode(handle),
        team_id=team.id,
    )
    dbsession.add(user)
    dbsession.flush()
    user.password = password
    dbsession.add(user)
    dbsession.flush()
    return user


def create_corporation(name, description="No description"):
    print(INFO + "Create corporation: " + bold + name + W)
    corp = Corporation(
        name=unicode(name),
        description=unicode(description),
    )
    dbsession.add(corp)
    dbsession.flush()
    return corp


def __mkipv4__(box, address):
    print(INFO + "IPv4 address '%s' now belongs to %s" % (address, box.name,))
    ip = IpAddress(
        v4=unicode(address),
    )
    box.ip_addresses.append(ip)
    dbsession.add(ip)
    dbsession.add(box)
    dbsession.flush()
    return ip


def __mkipv6__(box, address):
    print(INFO + "IPv6 address %s belongs to %s" % (
            address, str(bold+box.name+W),)
    )
    ip = IpAddress(
        v6=unicode(address),
    )
    box.ip_addresses.append(ip)
    dbsession.add(ip)
    dbsession.add(box)
    dbsession.flush()
    return ip


def create_box(name, corporation, difficulty, game_level,
                ipv4_addresses=[], ipv6_addresses=[]):
    print(INFO + "Create box: " + bold + name + W)
    box = Box(
        name=unicode(name),
        corporation_id=corporation.id,
        difficulty=unicode(difficulty),
        game_level_id=game_level.id,
    )
    dbsession.add(box)
    dbsession.flush()
    for ip_address in ipv4_addresses:
        __mkipv4__(box, ip_address)
    for ip_address in ipv6_addresses:
        __mkipv6__(box, ip_address)
    return box


def create_flag(name, token, value, box, description="No description",
                is_file=False, is_regex=False, is_hash=False):
    print(INFO + "Create flag: " + bold + name + W)
    flag = Flag(
        name=unicode(name),
        token=unicode(token),
        is_file=is_file,
        is_regex=is_regex,
        is_hash=is_hash,
        description=unicode(description),
        value=value,
        box_id=box.id,
    )
    dbsession.add(flag)
    dbsession.flush()