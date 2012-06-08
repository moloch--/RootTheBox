# -*- coding: utf-8 -*-
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

from libs.CachedTeam import CachedTeam

class CachedScores():
    
    def __init__(self):
        self.memory = {}
        
    def add_score(self, score_update):
        ''' This should change reclaculate the memory to add the update'''
        if not self.memory.has_key(score_update.team_name):
            self.memory[score_update.team_name] = CachedTeam(score_update)
        self.memory.get(score_update.team_name).add_score(score_update)

    def find_scores_by_team(self, team_name):
        try:
            scores = self.memory[team_name].scores
        except:
            scores = "[]"
        return scores
    
    def find_current_score_by_team(self, team_name):
        try:
            score = self.memory[team_name].current_score
        except:
            score = "0"
        return score