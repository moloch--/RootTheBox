# -*- coding: utf-8 -*-
'''
Created on Aug 26, 2013

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

This file wraps the Python scripted game setup API.
It reads an XML file(s) and calls the API based on the it's contents.

'''

import os
import logging
import setup.helpers as helpers
import xml.etree.cElementTree as ET

from base64 import b64decode
from libs.ConsoleColors import *
from tempfile import NamedTemporaryFile


def get_child_by_tag(elem, tag_name):
    ''' Return child elements with a given tag '''
    tags = filter(
        lambda child: child.tag == tag_name, elem.getchildren()
    )
    return tags[0] if 0 < len(tags) else None


def get_child_text(elem, tag_name):
    ''' Shorthand access to .text data '''
    return get_child_by_tag(elem, tag_name).text


def create_levels(levels):
    ''' Create GameLevel objects based on XML data '''
    logging.info("Found %s game level(s)" % levels.get('count'))
    for level_elem in levels.getchildren():
        if get_child_text(level_elem, 'number') != '0':
            helpers.create_game_level(
                number=get_child_text(level_elem, 'number'),
                buyout=get_child_text(level_elem, 'buyout'),
            )


def create_flags(parent, box):
    ''' Create flag objects for a box '''
    logging.info("Found %s flag(s)" % parent.get('count'))
    for flag_elem in parent.getchildren():
        helpers.create_flag(
            name=get_child_text(flag_elem, 'name'),
            token=get_child_text(flag_elem, 'token'),
            value=get_child_text(flag_elem, 'value'),
            box=box,
            description=get_child_text(flag_elem, 'description'),
            is_file=flag_elem.get('isfile') == 'True',
        )


def create_hints(parent, box):
    ''' Create flag objects for a box '''
    logging.info("Found %s hint(s)" % parent.get('count'))
    for hint_elem in parent.getchildren():
        helpers.create_hint(
            box=box,
            price=get_child_text('price'),
            description=get_child_text('description'),
        )


def _tmp_avatar(box_elem):
    ''' Decodes avatar data and writes to a tmp file '''
    data = b64decode(get_child_text(box_elem, 'avatar'))
    tmp_file = NamedTemporaryFile(delete=False)
    tmp_file.write(data)
    tmp_file.close()
    return tmp_file.name


def create_boxes(parent, corporation):
    ''' Create boxes for a corporation '''
    logging.info("Found %s boxes" % parent.get('count'))
    for box_elem in parent.getchildren():
        favatar = _tmp_avatar(box_elem)
        box = helpers.create_box(
            name=get_child_text(box_elem, 'name'),
            corporation=corporation,
            game_level=int(box_elem.get('gamelevel')),
            difficulty=get_child_text(box_elem, 'difficulty'),
            description=get_child_text(box_elem, 'description'),
            avatar=favatar,
        )
        os.unlink(favatar)
        create_flags(get_child_by_tag(box_elem, 'flags'), box)


def create_corps(corps):
    ''' Create Corporation objects based on XML data '''
    logging.info("Found %s corporation(s)" % corps.get('count'))
    for corp_elem in corps:
        corporation = helpers.create_corporation(
            name=get_child_text(corp_elem, 'name'),
            description=get_child_text(corp_elem, 'description'),
        )
        create_boxes(get_child_by_tag(corp_elem, 'boxes'), corporation)


def _xml_file_import(filename):
    ''' Parse and import a single XML file '''
    logging.info("Importing %s ... " % filename)
    try:
        tree = ET.parse(filename)
        xml_root = tree.getroot()
        levels = get_child_by_tag(xml_root, "gamelevels")
        create_levels(levels)
        corporations = get_child_by_tag(xml_root, "corporations")
        create_corps(corporations)
        logging.info("Imported %s successfully" % filename)
        return True
    except:
        logging.exception("Exception raised while parsing %s" % filename)
        return False


def import_xml(target):
    ''' Import XML file(s) '''
    target = os.path.abspath(target)
    if not os.path.exists(target):
        logging.error("Error: Target does not exist (%s) " % target)
    elif os.path.isdir(target):
        logging.info("%s is a directory ..." % target)
        ls = filter(lambda fname: fname.lower().endswith('.xml'), os.listdir(target))
        logging.info("Found %d XML file(s) ..." % len(ls))
        return [_xml_file_import(target+'/'+fxml) for fxml in ls]
    else:
        return _xml_file_import(target)
