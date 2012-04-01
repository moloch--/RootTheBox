
class CachedTeam():
    
    def __init__(self, update):
        self.team_name = update.team_name
        self.current_score = update.value
        self.scores = []
        
    def add_score(self, score_update):
        self.scores.append([int(score_update.time_stamp), self.current_score])
        self.current_score += int(score_update.value)
