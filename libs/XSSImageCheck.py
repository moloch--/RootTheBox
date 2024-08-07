# -*- coding: utf-8 -*-
"""
@author: moloch

    Copyright 2014

--------------------------------------------

Check for ticksy .gif and .bmp files
http://jklmnn.de/imagejs/

"""

import io
import os
from random import randint, sample
from string import printable
from pathlib import Path
import imghdr

from PIL import Image
from resizeimage import resizeimage
from tornado.options import options

from libs.ValidationError import ValidationError

MAX_AVATAR_SIZE = 1024 * 1024
MIN_AVATAR_SIZE = 64
IMG_FORMATS = ["png", "jpeg", "jpg", "gif", "bmp"]
IMG_SIZE = [500, 250]

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

def verify_image_size(image_data):
    image = Image.open(io.BytesIO(image_data))
    if image.width < IMG_SIZE[0] or image.height < IMG_SIZE[1]:
        raise ValidationError(
            "Image is too small, minimum size %d x %d"
            % (IMG_SIZE[0], IMG_SIZE[1])
        )

def avatar_validation(image_data) -> str:
    """Avatar validation check
    
    Returns image extension as str if checks pass
    """
    if MIN_AVATAR_SIZE < len(image_data) < MAX_AVATAR_SIZE:
        ext = imghdr.what("", h=image_data)
        if ext in IMG_FORMATS and not is_xss_image(image_data):
            verify_image_size(image_data)                                
            return ext
        else:
            raise ValidationError(
                "Invalid image format, avatar must be: %s"
                % (", ".join(IMG_FORMATS))
            )                
        
    else:
        raise ValidationError(
            "The image is too large must be %d - %d bytes"
            % (MIN_AVATAR_SIZE, MAX_AVATAR_SIZE)
        )
        
def save_avatar(path: str, image_data: bytes) -> str:
    """
    Save avatar image to path
    
    Returns image path without avatar_dir
    """
    try:
        base_path = Path(path)
        image_path = os.path.join(options.avatar_dir, base_path)
        
        if os.path.exists(image_path):
            os.unlink(image_path)
            
        image = Image.open(io.BytesIO(image_data))
        cover = resizeimage.resize_cover(image, IMG_SIZE)
        cover.save(image_path, image.format)
        return str(base_path)
        
    except Exception as e:
        raise ValidationError(e)