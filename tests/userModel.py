'''
Created on Mar 12, 2012

@author: moloch
'''

from hashlib import md5
from models import dbsession, User, Team

def test_create_user():
    user = User(
        user_name = unicode('joe'),
        display_name = unicode('moloch'),
        password = unicode('asdf'),
    )
    dbsession.add(user) #@UndefinedVariable
    dbsession.flush() #@UndefinedVariable
    
def test_by_user_name():
    user = User.by_user_name(unicode('joe'))
    assert not user == None
    hashTest = md5()
    hashTest.update(unicode('asdf'))
    assert user.password ==  hashTest.hexdigest()
    
def test_create_team():
    team = Team(
        team_name = unicode("The A Team"),
        motto = unicode("Pdc"),
        score = 0
    )
    dbsession.add(team) #@UndefinedVariable
    dbsession.flush() #@UndefinedVariable
    
def test_by_team_name():
    team = Team.by_team_name(unicode("The A Team"))
    assert not team == None
    
def test_add_user_to_team():
    team = Team.by_team_name(unicode("The A Team"))
    assert not team == None
    user = User.by_user_name(unicode("joe"))
    assert not user == None
    user.team_id = team.id
    dbsession.add(user) #@UndefinedVariable
    dbsession.flush() #@UndefinedVariable
    