#!/usr/bin/env python
'''
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
----------------------------------------------------------------------------

This file is the main starting point for the application, based on the 
command line arguments it calls various components setup/start/etc.

'''


import os
import sys
import logging
import argparse

from datetime import datetime
from libs.ConsoleColors import *


__version__ = 'Root the Box - v0.3.0'
current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def serve():
    ''' Starts the application '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from handlers import start_server
    print(INFO+'%s : Starting application ...' % current_time())
    start_server()


def create():
    ''' Creates/bootstraps the database '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from models import create_tables, boot_strap
    print(INFO+'%s : Creating the database ...' % current_time())
    create_tables()
    print(INFO+'%s : Bootstrapping the database ...' % current_time())
    try:
        boot_strap()
    except:
        print(WARN+"%s : Database has already been bootstrapped" % current_time())


def recovery():
    ''' Starts the recovery console '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from setup.recovery import RecoveryConsole
    print(INFO+'%s : Starting recovery console ...' % current_time())
    console = RecoveryConsole()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print(INFO + "Have a nice day!")


def setup_xml(xml_params):
    ''' Imports XML file(s) '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from setup.importers import import_xml
    for xml_param in xml_params:
        print(INFO+"Importing %s ..." % xml_param)
        import_xml(xml_param)
    print(INFO+"%s : XML import completed." % current_time())


def setup_script():
    ''' Imports a setup file '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    print(INFO+"%s : Running default setup file 'setup/game.py' ..." % current_time())
    try:
        from setup import game
        print(INFO+"%s : Setup file completed successfully." % current_time())
    except Exception as error:
        logging.exception("Game setup script raised an exception!")
        print(WARN+"Setup Error: Game script failed with "+str(error))
        sys.exit()

def test():
    print "Test has been fired"
    from setup import XmlGameImporter
    XmlGameImporter.import_xml_box_files_for_game("sample", 1)

def main(args):
    ''' Call functions in the correct order based on CLI params '''
    # Ensure that RootTheBox/ is the cwd
    rtb_root = os.path.abspath(__file__)
    rtb_cwd = os.path.dirname(rtb_root)
    if rtb_cwd != os.getcwd():
        print(INFO+"Switching CWD to %s" % rtb_cwd)
        os.chdir(rtb_cwd)
    # Create tables / bootstrap db
    if args.create_tables:
        create()
    # Execute game setup script
    if args.setup_script:
        setup_script()
    # Import any XML files
    if args.xml is not None:
        setup_xml(args.xml)
    # Start recovery console
    if args.recovery:
        recovery()
    # Start server
    if args.start_server:
        serve()
    # Run test functionality
    if args.run_test:
        test()

### Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Root the Box: A Game of Hackers',
    )
    parser.add_argument('-v', '--version',
        action='version',
        version=__version__,
    )
    parser.add_argument("-c", "--create-tables",
        action='store_true',
        dest='create_tables',
        help="create and initialize database tables (run once)",
    )
    parser.add_argument("-s", "--start",
        action='store_true',
        dest='start_server',
        help="start the server",
    )
    parser.add_argument("-x", "--xml",
        nargs='*',
        help="import xml file(s), or directory of file(s)",
    )
    parser.add_argument("-g", "--game-script",
        action='store_true',
        dest='setup_script',
        help="run a game setup script (setup/game.py)",
    )
    parser.add_argument(
        "-r", "--recovery",
        action='store_true',
        help="start the admin recovery console",
    )
    #TODO remove this before production
    parser.add_argument(
        "-t", "--test",
        action="store_true",
        dest='run_test',
        help="run testing code in the 'test' function (for debugging and development purposes)"
    )
    main(parser.parse_args())
