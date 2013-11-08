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

'''


import os
import imghdr
import logging

from uuid import uuid4
from libs.ConsoleColors import *
from models import dbsession, GameLevel, IpAddress, \
    Flag, Box, Corporation, User, Team, Hint


def create_game_level(number, buyout):
    ''' Creates a GameLevel object '''
    if GameLevel.by_number(number) is not None:
        logging.info("Game level #%s already exists, skipping" % number)
        return GameLevel.by_number(number)
    logging.info("Create Game Level #%s with a buyout of $%s" % (
        number, buyout
    ))
    new_level = GameLevel(
        number=abs(int(number)),
        buyout=abs(int(buyout)),
    )
    game_levels = GameLevel.all()
    game_levels.append(new_level)
    logging.debug("Updating game level linked list ...")
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
    if Team.by_name(name) is not None:
        logging.info("Team with name '%s' already exists, skipping" % (name))
        return Team.by_name(name)
    logging.info("Create Team: %s" % name)
    team = Team(
        name=unicode(name[:16]),
        motto=unicode(motto[:32]),
    )
    level_0 = GameLevel.all()[0]
    team.game_levels.append(level_0)
    dbsession.add(team)
    dbsession.flush()
    return team


def create_user(handle, password, bank_password, team):
    if User.by_handle(handle) is not None:
        logging.info("User with handle '%s' alreay exists, skipping" % (handle))
        return User.by_handle(handle)
    logging.info("Create User: %s" % handle)
    user = User(
        handle=unicode(handle[:16]),
        team_id=team.id,
    )
    dbsession.add(user)
    dbsession.flush()
    user.password = password
    user.bank_password = bank_password
    dbsession.add(user)
    dbsession.flush()
    return user


def create_corporation(name, description="No description"):
    if Corporation.by_name(name) is not None:
        logging.info("Corporation with name '%s' already exists, skipping" % (name))
        return Corporation.by_name(name)
    logging.info("Create Corporation: %s" % name)
    corp = Corporation(
        name=unicode(name[:32]),
        description=unicode(description[:1024]),
    )
    dbsession.add(corp)
    dbsession.flush()
    return corp


def __mkipv4__(box, address):
    logging.debug("IPv4 address '%s' now belongs to %s" % (address, box.name,))
    ip = IpAddress(
        v4=unicode(address),
    )
    box.ip_addresses.append(ip)
    dbsession.add(ip)
    dbsession.add(box)
    dbsession.flush()
    return ip


def __mkipv6__(box, address):
    logging.debug("IPv6 address %s belongs to %s" % (
        address, box.name,
    ))
    ip = IpAddress(
        v6=unicode(address),
    )
    box.ip_addresses.append(ip)
    dbsession.add(ip)
    dbsession.add(box)
    dbsession.flush()
    return ip


def create_box(name, corporation, difficulty, game_level, description,
        ipv4_addresses=[], ipv6_addresses=[], avatar=None):
    if Box.by_name(name) is not None:
        logging.info("Box with name '%s' already exists, skipping" % (name))
        return Box.by_name(name)
    logging.info("Create Box: %s" % name)
    if isinstance(game_level, int):
        game_level = GameLevel.by_number(game_level)
    box = Box(
        name=unicode(name[:16]),
        corporation_id=corporation.id,
        difficulty=unicode(difficulty[:16]),
        game_level_id=game_level.id,
        _description=unicode(description[:1024]),
    )
    dbsession.add(box)
    dbsession.flush()
    if avatar is not None and os.path.exists(avatar):
        set_avatar(box, avatar)
    for ip_address in ipv4_addresses:
        __mkipv4__(box, ip_address)
    for ip_address in ipv6_addresses:
        __mkipv6__(box, ip_address)
    return box
    

def set_avatar(box, favatar):
    '''
    Saves avatar - Reads file header and only allows approved formats
    '''
    f = open(favatar, 'r')
    data = f.read()
    if 0 < len(data) < (1024 * 1024):
        if box.avatar == "default_avatar.jpeg":
            box.avatar = unicode(uuid4()) + u".jpeg"
        ext = imghdr.what("", h=data)
        avatar_path = 'files/avatars/' + box.avatar
        if ext in ['png', 'jpeg', 'gif', 'bmp']:
            if os.path.exists(avatar_path):
                os.unlink(avatar_path)
            box.avatar = unicode(box.avatar[:box.avatar.rfind('.')] + "." + ext)
            file_path = 'files/avatars/'+box.avatar
            avatar = open(file_path, 'wb')
            avatar.write(data)
            avatar.close()
            dbsession.add(box)
            dbsession.flush()
    f.close()


def create_flag(name, token, value, box, _type, description="No description", is_file=False):
    if Flag.by_name(name) is not None:
        logging.info("Flag with name '%s' already exists, skipping" % (name))
        return Flag.by_name(name)
    if Flag.by_token(token) is not None:
        logging.info("Flag with token '%s' already exists, skipping" % (token))
        return Flag.by_token(token)
    if is_file and os.path.exists(token):
        with open(token) as favatar:
            _token = Flag.digest(favatar.read())
    elif is_file and 40 == len(token):
        _token = unicode(token)  # Just assume it's a SHA1
    elif is_file:
        raise ValueError("Flag token file does not exist, and is not a hash.")
    else:
        _token = unicode(token[:256])
    if _type not in Flag.FLAG_TYPES:
        raise ValueError('Invalid flag type "%s"' % _type)
    logging.info("Create Flag: %s" % name)
    flag = Flag(
        name=unicode(name[:32]),
        token=unicode(_token),
        _type=unicode(_type),
        description=unicode(description[:256]),
        value=abs(int(value)),
        box_id=box.id,
    )
    dbsession.add(flag)
    dbsession.flush()
    return flag


def create_hint(box, price, description):
    logging.info("Create Hint: %s has a new hint for $%s" % (box.name, price,))
    hint = Hint(
        box_id=box.id,
        price=abs(int(price)),
        description=unicode(description[:256])
    )
    dbsession.add(hint)
    dbsession.flush()
    return hint