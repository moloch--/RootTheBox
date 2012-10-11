# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

@author: moloch

 Copyright 2012 Root the Box

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


from models import dbsession, User, WallOfSheep
from libs.Notifier import Notifier
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler


class HashesHandler(BaseHandler):
    ''' Displays user password hashes '''

    MIN_ACCOUNT = 100

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders hashes page '''
        self.render_page()

    @authenticated
    def post(self, *args, **kwargs):
        ''' Submit cracked hashes get checked '''
        handle = self.get_argument("handle", default="")
        preimage = self.get_argument("preimage", default="")
        user = User.by_id(self.session['user_id'])
        target = User.by_handle(handle)
        if target is None or user is None or target.has_permission("admin"):
            self.render_page(errors=["That user does not exist"])
        elif target in user.team.members:
            self.render_page(errors=["We got a badass over here; trying to crack his own team's hashes"])
        elif target.money <= self.MIN_ACCOUNT:
            self.render_page(errors=["Target user's team must have a bank account balance greater than %d" % self.MIN_ACCOUNT])
        elif target.validate_password(preimage):
            stolen_money = self.steal_money(user, target)
            self.add_to_wall(user, target, preimage, stolen_money)
            message = "%s hacked %s's bank account and stole $%d" % (user.handle, target.team.name, stolen_money)
            Notifier.broadcast_custom("Bank Account Hacked", message, "/avatars/"+user.avatar)
            message = "%s cracked your password, maybe you should change it..." % (user.handle,)
            Notifier.user_warning(target, "Cracked Password", message)
            self.render("hashes/success.html", user=user, target=target)
        else:
            self.render_page(errors=["Wrong password, try again"])

    def render_page(self, errors=None):
        ''' Small wrapper for render() to automatically pass in args '''
        user = User.by_id(self.session['user_id'])
        self.render(
            "hashes/view.html", errors=errors, current_team=user.team)

    def add_to_wall(self, user, target, preimage, value):
        ''' Creates an entry in the wall of sheep '''
        sheep = WallOfSheep(
            preimage=unicode(preimage),
            point_value=value,
            user_id=target.id,
            cracker_id=user.id
        )
        dbsession.add(sheep)
        dbsession.flush()

    def steal_money(self, user, target):
        ''' Steal the money '''
        steal_value = target.team.money
        user.team.money += int(target.team.money - (target.team.money * 0.15))
        target.team.money = 0
        dbsession.add(user.team)
        dbsession.add(target.team)
        dbsession.flush()
        return steal_value


class HashesAjaxHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders a user details div, requested via AJAX '''
        user = self.get_current_user()
        handle = self.get_argument("handle", default="")
        target = User.by_handle(handle)
        if user is None or target in user.team.members:
            self.write({"Error":"No Data"})
        elif user.has_item("New York Federal Reserve"):
            self.render({target.handle:target.password})
        else:
            self.write({"Error":"No Data"})

