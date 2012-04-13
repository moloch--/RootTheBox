# -*- coding: utf-8 -*-
"""
this serves as a 'loader' for some commonly basic use function
every womyn (or man) needs in the process of a web app development

it's called __\_\_main\_\_.py__ so u'll be able to type 'python . [command]'
and it'll fulfill your wishes.

feel free to change the filename if you wish.
as I said before. nothing in this template is hardcoded
"""

from os import system
from sys import argv
from time import sleep
from datetime import datetime
from subprocess import call
from handlers import start_game
from models import __create__, __boot_strap__

curr_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]

def serve():
    """
    serves the application
    ----------------------
    """
    if len(argv) == 2:
        print('=> %s : Starting up the application, please wait ...' % curr_time())
        start_game()

def create():
    """
    creates the database
    --------------------
    """
    # Create the table schemas
    # usage: python . create 
    
    #Bootstrap the database with some objects
    #usage: python . create bs
    print('=> %s : creating the database.'%curr_time())
    __create__()
    if len(argv) == 3 and argv[2] == 'bs':
        __boot_strap__()
    
def test():
    """
    run unit tests
    ---------------------
    """
    # usage: python . test
    print '=> %s : testing the application.' % curr_time()
    # calling nose's nosetests to test the application using the 'tests' module
    call(['nosetests', '-v', 'tests'])
    
# -----
if len(argv) == 1:
    argv.append("serve")
options = ['serve', 'create', 'test']
if argv[1] in options:
    eval(argv[1])()
else:
    print '[!] Error: PEBKAC'
