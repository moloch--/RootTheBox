# -*- coding: utf-8 -*-
'''
Created on April 1, 2012

@author: moloch

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
                self.render("challenges/ajax_list.html",
                            challenges=Challenge.get_all())
        else:
            challenge = Challenge.by_id(challenge_id)
            if challenge != None:
                self.render(
                    "challenges/ajax_challenge.html", challenge=challenge)
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
        self.render("challenges/view.html", challenges=correct_challenges)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Compares submitted token to stored token '''
        try:
            token = self.get_argument("token")
        except:
            self.render("user/error.html", operation="Submit Challenge",
                        errors="Please enter a token")
        try:
            challenge_id = self.get_argument("challenge_id")
            logging.info("Got: " + str(challenge_id))
            challenge = Challenge.by_id(self.get_argument("challenge_id"))
            if challenge == None:
                raise TypeError
        except:
            self.render("user/error.html",
                        operation="Submit Challenge", errors="Invalid challenge")
        user = User.by_user_name(self.session.data['user_name'])
        if user != None and user.team != None:
            logging.info("%s submitted a token for challenge '%s'" %
                         (user.user_name, challenge.name))
            if not challenge in user.team.challenges:
                if token == challenge.token:
                    action = Action(
                        classification=unicode("Challenge Completed"),
                        description=unicode(user.user_name +
                                            " has succesfully completed " + challenge.name),
                        value=challenge.value,
                        user_id=user.id
                    )
                    challenge.teams.append(user.team)
                    self.dbsession.add(challenge)
                    self.dbsession.add(action)
                    self.dbsession.flush()
                    self.render("challenges/success.html")
                else:
                    self.render("user/error.html", operation="Submit Challenge",
                                errors="Invalid Token")
            else:
                self.render("user/error.html", operation="Submit Challenge",
                            errors="This challenge was already completed")
        else:
            self.redirect("/login")
