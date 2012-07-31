'''
Created on Mar 21, 2012

@author: haddaway

 Copyright [2012] [Redacted Labs]

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

import logging
from libs.Singleton import *
from libs.Session import SessionManager
from models.SEChallenge import SEChallenge


@Singleton
class SEManager():

    def __init__(self):
        self.last_challenge = None
        self.active_challenge = SEChallenge.get_lowest()

    def update_challenge(self):
        self.last_challenge = self.active_challenge
        self.active_challenge = SEChallenge.get_by_level(
            self.active_challenge.level + 1)

    def get_current(self):
        correct = SEChallenge.get_highest()
        if self.active_challenge == None and correct != None and self.last_challenge != None:
            if self.last_challenge.level < correct.level:
                self.active_challenge = correct
        return self.active_challenge
