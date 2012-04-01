
from libs.CachedTeam import CachedTeam

'''
This is a wrapper for an entire section of the scoreboard that we will ajax in
'''
class CachedScores():
    
    def __init__(self):
        self.memory = {}
        
    def add_score(self, score_update):
        ''' This should change reclaculate the memory to add the update'''
        if not self.memory.has_key(score_update.team_name):
            self.memory[score_update.team_name] = CachedTeam(score_update)
        else:
            self.memory.get(score_update.team_name).add_score(score_update)

    def find_scores_by_team(self, team_name):
        return self.memory[team_name].scores