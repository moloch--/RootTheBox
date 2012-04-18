'''
Created on Mar 17, 2012

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

from jsonpickle.pickler import Pickler

class ScoreUpdate():
    
    def __init__(self, time_stamp, value, team_name):
        self.time_stamp = str(time_stamp)
        self.value = str(value)
        self.team_name = str(team_name)
    
    def to_message(self):
        return Pickler().flatten(self)
