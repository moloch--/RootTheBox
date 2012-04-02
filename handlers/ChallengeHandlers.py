'''
Created on April 1, 2012

@author: moloch
'''

from tornado.web import RequestHandler
from models import User, Action, Challenge
from libs.SecurityDecorators import authenticated
from BaseHandlers import UserBaseHandler

class ChallengesAjaxHandler(RequestHandler):

    def initialize(self, dbsession):
        self.dbsession = dbsession

    @authenticated
    def get(self, *args, **kwargs):
        try:
            challenge_id = self.get_argument("id")
        except:
            self.write("No Data")
        if challenge_id == "back":
                self.render("challenges/ajax_list.html", challenges = Challenge.get_all())
        else:
            challenge = Challenge.by_id(challenge_id)
            if challenge != None:
                self.render("challenges/ajax_challenge.html", challenge = challenge)
            else:
                self.write("No Data")

class ChallengesHandler(UserBaseHandler):
    
    @authenticated
    def get(self, *args, **kwargs):
        user = User.by_user_name(self.session.data['user_name'])
        all_challenges = Challenge.get_all()
        correct_challenges = []
        for challenge in all_challenges:
            if user.team != None and not challenge in user.team.challenges:
                correct_challenges.append(challenge)
        self.render("challenges/view.html", challenges = correct_challenges)
    
    @authenticated
    def post(self, *args, **kwargs):
        user = User.by_user_name(self.session.data['user_name'])
        try:
            token = self.get_argument("token")
            challenge = Challenge.get_by_id(self.get_argument("challenge"))
        except:
            self.render("user/error.html", operation = "Submit Challenge", errors = "Please enter a token")    
        if user.team != None:
            if not challenge in user.team.challenges:
                if token == challenge.token:
                    action = Action(
                        classification = unicode("Challenge Completed"),
                        description = unicode(user.user_name+" has succesfully completed "+challenge.name),
                        value = challenge.value,
                        user_id = user.id
                    )
                    challenge.teams.append(user.team)
                    self.dbsession.add(challenge)
                    self.dbsession.add(action)
                    self.dbsession.flush()
                    self.redirect('/challenge')
                else:
                    self.render("user/error.html", operation = "Submit Challenge", errors = "Invalid Token")
            else:
                self.render("user/error.html", operation = "Submit Challenge", errors = "This challenge was already completed")
        else:
            self.render("user/error.html", operation = "Submit Challenge", errors = "You're not on a team")
