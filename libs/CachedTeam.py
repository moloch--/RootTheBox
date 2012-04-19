'''

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
class CachedTeam():
    
    def __init__(self, update):
        self.team_name = update.team_name
        self.current_score = 0
        self.scores = []
        
        
    def add_score(self, score_update):
        self.current_score += int(score_update.value)
        self.scores.append([int(score_update.time_stamp), self.current_score])
