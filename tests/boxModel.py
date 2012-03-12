'''
Created on Mar 12, 2012

@author: moloch
'''

from models import dbsession, Box

def test_create_box():
    box = Box(
        box_name = unicode('The Gibson'),
        ip_address = unicode('127.0.0.1'),
        description = unicode('A Super Computer'),
        root_key = unicode('123456'),
        root_value = 50,
        user_key = unicode('654321'),
        user_value = 25
    )
    dbsession.add(box) #@UndefinedVariable
    dbsession.flush() #@UndefinedVariable

def test_by_box_name():
    box = Box.by_box_name(unicode('The Gibson'))
    assert box.ip_address == unicode('127.0.0.1')
    box2 = Box.by_ip_address(unicode(''))
    assert box2 == None

def test_by_ip_address():
    box = Box.by_ip_address(unicode('127.0.0.1'))
    assert box.box_name == unicode('The Gibson')
    box2 = Box.by_ip_address(unicode(''))
    assert box2 == None