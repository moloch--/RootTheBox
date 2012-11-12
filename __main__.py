# -*- coding: utf-8 -*-
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
'''


from os import system, path
from sys import argv
from time import sleep
from datetime import datetime
from libs.ConsoleColors import *


current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def serve():
    ''' Starts the application '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from handlers import start_server
    print(INFO + '%s : Starting application ... ' %
          current_time())
    start_server()


def create():
    ''' Creates/bootstraps the database '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from models import create_tables, boot_strap
    print(INFO + '%s : Creating the database ... ' %
          current_time())
    create_tables()
    if len(argv) == 3 and (argv[2] == 'bootstrap' or argv[2] == '-b'):
        print('\n\n\n' + INFO +
              '%s : Bootstrapping the database ... \n' % current_time())
        boot_strap()


def recovery():
    ''' Starts the recovery console '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from setup.recovery import RecoveryConsole
    print(INFO + '%s : Starting recovery console ... ' %
          current_time())
    console = RecoveryConsole()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print(INFO + "Have a nice day!")

def setup():
    ''' Imports a setup file '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    if 3 == len(argv) and path.exists(argv[2]) and path.isfile(argv[2]):
        print(INFO + "%s : Import setup file '%s' ..." % (current_time(), argv[2]))
        __import__(argv[2])
    elif 3 == len(argv):
        print(WARN + "File not found: %s" % argv[1])
    else:
        print(INFO + "%s : Running default setup file 'setup/game.py' ..." % (current_time(),))
        from setup import game
        print(INFO + "Setup file completed.")

def help():
    ''' Displays a helpful message '''
    print('\n\t\t' + bold + R + "*** " + underline +
          'Root the Box: A Game of Hackers' + W + bold + R + " ***" + W)
    print('\t' + bold + 'python . help' + W +
          '             - Display this helpful message')
    print('\t' + bold + 'python . serve' + W +
          '            - Starts the web server')
    print('\t' + bold + 'python . create' + W +
          '           - Inits the database tables only')
    print('\t' + bold + 'python . create bootstrap' + W +
          ' - Inits the database tables and creates an admin account')
    print('\t' + bold + 'python . recovery' + W +
          '         - Starts the recovery console')
    print('\t' + bold + 'python . setup <file>' + W +
          '     - Runs a game setup script from "setup/game.py" or <file>')

### Main
if __name__ == '__main__':
    options = {
        'help': help,
        'serve': serve,
        'start': serve,
        'create': create,
        'recovery': recovery,
        'setup': setup,
    }
    if len(argv) == 1:
        help()
    else:
        if argv[1] in options:
            options[argv[1]]()
        else:
            print(WARN + 'PEBKAC (%s): Command not found, see "python . help".' % argv[1])