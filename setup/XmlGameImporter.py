# -*- coding: utf-8 -*-
'''
Created on Aug 26, 2013

@author lavalamp

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

from os import path, _exit, listdir
from sqlalchemy.exc import OperationalError
import sys
import xml.etree.cElementTree as ET
from libs.ConsoleColors import *
from models import dbsession, Sponsor, Corporation,\
    Flag, Box

def print_info(information):
    print(INFO+"Info: " + information)

def print_success(success):
    print(INFO+"Success: " + success)

def print_warning_and_exit(warning):
    print(WARN+"Error: " + warning)
    _exit(1)

def validate_xml_box_file(filepath):
    #TODO validate entire file
    return []

#TODO don't use hard-coded game directory, allow for configuration elsewhere
def import_xml_box_files_for_game(game_name, input_game_level_id):
    game_dir = path.abspath('games/' + game_name)
    for curfile in listdir(game_dir):
        if curfile.endswith('.xml'):
            import_xml_box_file(game_dir + '/' + curfile, input_game_level_id)

#TODO include IP addresses
def import_xml_box_file(filepath, input_game_level_id):
    
    print_info("Starting import of file " + filepath)
    
    errors = validate_xml_box_file(filepath)
    if len(errors) > 0:
        for ind, error in enumerate(errors):
            print "Error " + str(ind) + ": " + error
        print_warning_and_exit("XML file was not valid.")

    try:
        #TODO process uploading image files
        tree = ET.parse(filepath)
        root = tree.getroot()
            
        # Get information for sponsor
        sponsornode = root[0]
        sname = sponsornode.find('name').text
        sdesc = sponsornode.find('description').text
        surl = sponsornode.find('url').text
        slogo = sponsornode.find('logo').text
        
        # Create the sponsor object and add it to the dbobject list
        #TODO check if sponsor already exists
        spon = Sponsor(
            name=unicode(sname),
            logo=unicode(slogo),
            description=unicode(sdesc),
            url=unicode(surl)
        )
        
        # Add the sponsor to the DB
        dbsession.add(spon)
        dbsession.flush()
        
        # Get the corporation information
        #TODO check if corporation already exists
        corpnode = root[1]
        corpname = corpnode.find('name').text
        corpdesc = corpnode.find('description').text
        
        # Create the corporation object and add it to the dbobject list
        corp = Corporation(
            name=unicode(corpname),
            description=unicode(corpdesc)
        )
            
        # Add the corporation to the DB
        dbsession.add(corp)
        dbsession.flush()
            
        # Get box's name
        boxname = root[2].text
        
        # Get box's difficulty
        boxdiff = root[3].text
        
        # Get box's avatar file
        boxavatarpreprocess = root[4].text
        #TODO upload avatar and get proper url
        boxavatar = boxavatarpreprocess
        
        # Get the box's description
        boxdesc = root[5].text
        
        # Create the box
        newbox = Box(
            name=unicode(boxname),
            corporation_id=corp.id,
            difficulty=unicode(boxdiff),
            game_level_id=input_game_level_id,
            _description=unicode(boxdesc),
            avatar=unicode(boxavatar),
            sponsor_id=spon.id
        )
        
        # Add the box to the DB
        dbsession.add(newbox)
        dbsession.flush()
        
        # Iterate through flags
        flags = []
        for curflagnode in root[6]:
            curflagname = curflagnode.find('name').text
            curflagtoken = curflagnode.find('token').text
            curflagdesc = curflagnode.find('description').text
            curflagvalue = curflagnode.find('value').text
            newflag = Flag(
                name=unicode(curflagname),
                token=unicode(curflagtoken),
                is_file=False, #TODO implement file upload stuff
                description=unicode(curflagdesc),
                value=abs(int(curflagvalue)),
                box_id=newbox.id
            )
            flags.append(newflag)
            
        # Add all the flags to the database
        for curflag in flags:
            dbsession.add(curflag)
        dbsession.flush()
        
        # Notify user that import has succeeded
        print_success("Import of file " + filepath + " finished without issue.")
    except OperationalError as e:
        print "OperationalError thrown: " + str(e)
    except ET.ParseError as e:
        print "ParseError thrown: " + str(e)
    except:
        print_warning_and_exit("Unexpected error:" + str(sys.exc_info()[0]))
        pass
