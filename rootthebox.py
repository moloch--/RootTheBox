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
import nose
import random
import logging
import argparse

from datetime import datetime
from libs.ConsoleColors import *


__version__ = 'Root the Box - v0.4.0'
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
    print(INFO+'%s : Creating the database ...' % current_time())
    from setup.create_database import create_tables, engine, metadata
    is_devel = ConfigManager.instance().bootstrap.startswith('dev')
    create_tables(engine, metadata, is_devel)
    print(INFO+'%s : Bootstrapping the database ...' % current_time())
    import setup.bootstrap
    # Display Details
    if is_devel:
        environ = bold + R + "Developement boot strap" + W
        details = ", admin password is 'nimda123'."
    else:
        environ = bold + "Production boot strap" + W
        details = '.'
    print(INFO + '%s completed successfully%s' % (environ, details))


def recovery():
    ''' Starts the recovery console '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from setup.recovery import RecoveryConsole
    print(INFO+'%s : Starting recovery console ...' % current_time())
    console = RecoveryConsole()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print(INFO+"Have a nice day!")


def setup_xml(xml_params):
    ''' Imports XML file(s) '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from setup.xmlsetup import import_xml
    for index, xml_param in enumerate(xml_params):
        print(INFO + "Processing %d of %d .xml file(s) ..." % (index + 1, len(xml_params)))
        import_xml(xml_param)
    print(INFO+"%s : Completed processing of all .xml file(s)" % current_time())


def tests():
    ''' Creates a temporary sqlite database and runs the unit tests '''
    print(INFO+'%s : Running unit tests ...' % current_time())
    from tests import setup_database, teardown_database
    db_name = 'test-%04s' % random.randint(0, 9999)
    setup_database(db_name)
    nose.run(module='tests', argv=[os.getcwd() + '/tests'])
    teardown_database(db_name)


def restart_serve():
    ''' Shutdown the actual process and restart the service. Useful for rootthebox.cfg changes. '''
    pid = os.getpid()
    print(INFO+'%s : Restarting the service (%i)...' % (current_time(), pid) )
    os.execl('./setup/restart.sh', '')


def main(args):
    ''' Call functions in the correct order based on CLI params '''
    # Ensure that RootTheBox/ is the cwd
    rtb_root = os.path.abspath(__file__)
    rtb_cwd = os.path.dirname(rtb_root)
    if rtb_cwd != os.getcwd():
        print(INFO + "Switching CWD to '%s'" % rtb_cwd)
        os.chdir(rtb_cwd)
    # Run unit tests
    if args.run_tests:
        tests()
    # Create tables / bootstrap db
    if args.create_tables:
        create()
    # Import any XML files
    if args.xml is not None:
        setup_xml(args.xml)
    # Start recovery console
    if args.recovery:
        recovery()
    # Start server
    if args.restart_service:
        restart_serve()
    elif args.start_server:
        serve()

### Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Root the Box: A Game of Hackers',
    )
    parser.add_argument("-v", "--version",
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
    parser.add_argument("-t", "--tests",
        action='store_true',
        dest='run_tests',
        help="run unit tests (developement only)",
    )
    parser.add_argument("-x", "--xml",
        nargs='*',
        help="import xml file(s), or directories of xml files",
    )
    parser.add_argument("-r", "--recovery",
        action='store_true',
        help="start the admin recovery console",
    )
    parser.add_argument("-R", "--restart",
        action='store_true',
        dest='restart_service',
        help="restart the service",
    )
    main(parser.parse_args())
