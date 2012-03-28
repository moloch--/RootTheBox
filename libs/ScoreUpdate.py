'''
Created on Mar 17, 2012

@author: haddaway
'''

from jsonpickle.pickler import Pickler

class ScoreUpdate():
    
    def __init__(self, time_stamp, value, team_name):
        self.time_stamp = str(time_stamp)
        self.value = str(value)
        self.team_name = str(team_name)
    
    def to_message(self):
        return Pickler().flatten(self)
