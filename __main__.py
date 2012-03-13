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
curr_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]

def serve():
    """
    serves the application
    ----------------------
    """
    # usage: python . serve
    
    # spwans a process of this 'loader', which starts the applicaion by importing the \_\_serve\_\_ method.
    if len(argv) == 2:
        print('=> %s : serving the application.' % curr_time())
        system('python . serve now')
        try: 
            sleep(-1)
        except: 
            pass
    # checkout handlers/__\_\_init\_\_.py__
    else:
        from handlers import __serve__
        __serve__()

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
    from models import __create__, __boot_strap__
    __create__()
    if(len(argv) == 3):
        if(argv[2] == 'bs'):
            __boot_strap__()
    
def test():
    """
    tests the application
    ---------------------
    """
    # usage: python . test
    print('=> %s : testing the application.' % curr_time())
    # calling nose's nosetests to test the application using the 'tests' module
    call(['nosetests', '-v', 'tests'])

def docs():
    """
    documents the project
    ---------------------
    """
    # usage: python . docs
    print('=> %s : documenting in process.' % curr_time())
    # calling pycco to document the this project
    directories = ['.', 'handlers', 'libs', 'models', 'setup', 'tests']
    call(['pycco', '-p'] + map(lambda directory: directory + '/*.py', directories))
    
# -----
if len(argv) == 1:
    argv.append("serve")
# _the optional commands:_
options = ['serve', 'create', 'test', 'docs']
# evaling the command. if invalid command will print out a nicely formatted 'help' table
#if len(argv) == 1 or argv[1] not in options:
#    print('')
#    for option in options: print('  ->\t%s\t%s'%(option, eval(option).__doc__.split('\n')[1]))        

eval(argv[1])()