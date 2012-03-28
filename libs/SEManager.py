'''
Created on Mar 21, 2012

@author: haddaway
'''
from libs.Singleton import *
import logging
from libs.Session import SessionManager
import models
from models.SEChallenge import SEChallenge

@Singleton
class SEManager():
    
    def __init__(self):
        self.last_challenge = None
        self.active_challenge = SEChallenge.get_lowest()
    
    def update_challenge(self):
        self.last_challenge = self.active_challenge
        self.active_challenge = SEChallenge.get_by_level(self.active_challenge.level+1)
        
    def get_current(self):
        correct = SEChallenge.get_highest()
        if self.active_challenge == None:
            if self.last_challenge.level < correct.level:
                self.active_challenge = correct
        return self.active_challenge