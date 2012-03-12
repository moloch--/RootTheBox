'''
Created on Mar 12, 2012

@author: moloch
'''

from models import dbsession, Box


class BoxTests():
    # User Account
    
    
    def createTest(self):
        box = Box(
            box_name = 'The Gibson',
            ip_address = '127.0.0.1',
            description = 'A Super Computer',
            root_key = '123456',
            root_value = 50,
            user_key = '654321',
            user_value = 25
        )
        dbsession.add(box) #@UndefinedVariable
        dbsession.flush() #@UndefinedVariable
        print 'GOT THIS FAR?!?!?!'
        assert True