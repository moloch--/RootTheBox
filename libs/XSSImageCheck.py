# -*- coding: utf-8 -*-
"""
@author: moloch

    Copyright 2014

--------------------------------------------

Check for ticksy .gif and .bmp files
http://jklmnn.de/imagejs/

"""

import os
from string import printable
from tornado.options import options
from random import randint, sample

MAX_AVATAR_SIZE = 1024 * 1024
MIN_AVATAR_SIZE = 64
IMG_FORMATS = ["png", "jpeg", "jpg", "gif", "bmp"]


def is_xss_image(data):
    # str(char) works here for both py2 & py3
    return all([str(char) in printable for char in data[:16]])


def get_new_avatar(dir, forceteam=False):
    avatar = default_avatar(dir)
    avatars = filter_avatars(dir)
    if len(avatars) == 0:
        return avatar
    if dir == "team" or forceteam:
        from models.Team import Team

        cmplist = Team.all()
    elif dir == "user":
        from models.User import User

        cmplist = User.all()
    else:
        from models.Box import Box

        cmplist = Box.all()
    dblist = [item._avatar for item in cmplist if item._avatar]
    for image in avatars:
        if image not in dblist:
            return image
    return avatars[randint(0, len(avatars) - 1)]


def default_avatar(dir):
    if dir == "team":
        avatar = "default_team.jpg"
    elif dir == "user":
        avatar = "default_user.jpg"
    else:
        avatar = "default_box.jpg"
    return avatar


def filter_avatars(dir):
    avatars = os.listdir(options.avatar_dir + "/" + dir)
    avatarlist = []
    for avatar in avatars:
        if avatar.lower().endswith(tuple(IMG_FORMATS)):
            avatarlist.append(dir + "/" + avatar)
    return sample(avatarlist, len(avatarlist))


def existing_avatars(dir):
    avatars = []
    if dir == "team":
        from models.Team import Team

        teams = Team.all()
        for team in teams:
            if team.avatar is not None and len(team.members) > 0:
                avatars.append(team.avatar)
    else:
        from models.User import User

        users = User.all()
        for user in users:
            if user.avatar is not None:
                avatars.append(user.avatar)
    return avatars
