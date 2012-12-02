# -*- coding: utf-8 -*-
'''
Created on Sep 25, 2012

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


from BaseHandlers import BaseHandler
from models import dbsession, User, WallOfSheep, Team
from libs.Form import Form
from libs.SecurityDecorators import authenticated, has_item, debug


class PasswordSecurityHandler(BaseHandler):
    ''' Renders views of items in the market '''

    @authenticated
    @has_item("Password Security")
    def get(self, *args, **kwargs):
        ''' Render update hash page '''
        self.render_page()

    @authenticated
    @has_item("Password Security")
    def post(self, *args, **kwargs):
        ''' Attempt to upgrade hash algo '''
        form = Form(
            old_password="Enter your existing password",
            new_password1="Enter a new password",
            new_password2="Confirm your new password",
        )
        user = self.get_current_user()
        passwd = self.get_argument('new_password1')
        old_passwd = self.get_argument('old_password')
        if form.validate(self.request.arguments):
            if not user.validate_password(old_passwd):
                self.render_page(["Invalid password"])
            elif not passwd == self.get_argument('new_password2'):
                self.render_page(["New passwords do not match"])
            elif len(passwd) <= self.config.max_password_length:
                self.update_password(passwd)
                self.render_page()
            else:
                self.render_page(["New password is too long"])
        else:
            self.render_page(form.errors)

    def render_page(self, errors=None):
        user = self.get_current_user()
        self.render('upgrades/password_security.html',
            errors=errors, user=user
        )

    def update_password(self, new_password):
        '''
        Update user to new hashing algorithm and then updates the password
        using the the new algorithm
        '''
        user = self.get_current_user()
        user.algorithm = user.next_algorithm()
        dbsession.add(user)
        dbsession.flush()
        user.password = new_password
        dbsession.add(user)
        dbsession.flush()


class FederalReserveHandler(BaseHandler):

    @authenticated
    @has_item("Federal Reserve")
    def get(self, *args, **kwargs):
        self.render_page(None)

    @authenticated
    @has_item("Federal Reserve")
    def post(self, *args, **kwargs):
        ''' Attempt to steal money '''
        form = Form(
            handle="Please select a user",
            password="Please enter a password"
        )
        if form.validate(self.request.arguments):
            victim = User.by_handle(self.get_argument('handle'))
            if victim is not None:
                if victim.validate_password(self.get_argument('password')):
                    self.theft(victim)
                    self.render('upgrades/theft.html')
                else:
                    self.render_page(["Incorrect password, try again."])
            else:
                self.render_page(["User does not exist."])
        else:
            self.render_page(form.errors)

    def render_page(self, errors):
        ''' Wraps self.render to add params '''
        user = self.get_current_user()
        self.render('upgrades/federal_reserve.html', user=user, errors=errors)

    def theft(self, victim):
        ''' Successfully cracked a password '''
        user = self.get_current_user()
        value = int(victim.team.money * 0.85)
        password = self.get_argument('password')
        user.team.money += value
        victim.team.money = 0
        dbsession.add(user.team)
        dbsession.add(victim.team)
        sheep = WallOfSheep(
            preimage=unicode(password),
            cracker_id=user.id,
            victim_id=victim.id,
        )
        dbsession.add(sheep)
        dbsession.flush()
        self.event_manager.cracked_password(user, victim, password, value)


class FederalReserveAjaxHandler(BaseHandler):

    @debug
    def get(self, *args, **kwargs):
        commands = {
            'ls': self.ls,
        }
        if 0 < len(args) and args[0] in commands:
            commands[args[0]]()
        else:
            self.render("public/404.html")

    @debug
    def ls(self):
        if self.get_argument('data').lower() == 'accounts':
            self.write({'accounts': [team.name for team in Team.all()]})
        else:
            self.write({'Error': 'Invalid data type'})
        self.finish()


class SourceCodeMarketHandler(BaseHandler):

    @authenticated
    @has_item("Source Code Market")
    def get(self, *args, **kwargs):
        self.render('upgrades/source_code_market.html', errors=None)

    @authenticated
    @has_item("Source Code Market")
    def post(self, *args, **kwargs):
        form = Form(
            source_uuid="Please select leaked code to buy",
        )
        if form.validate(self.request.arguments):
            pass
        else:
            self.render('upgrades/source_code_market.html', errors=form.errors)


class SwatHandler(BaseHandler):

    @authenticated
    @has_item("SWAT")
    def get(self, *args, **kwargs):
        self.render('upgrades/swat.html', errors=None)

    @authenticated
    @has_item("SWAT")
    def post(self, *args, **kwargs):
        form = Form(
            handle="Please select a target to SWAT",
            bribe="Please enter a bribe",
        )
        if form.validate(self.request.arguments):
            pass
        else:
            self.render('upgrades/swat.html', errors=form.errors)
