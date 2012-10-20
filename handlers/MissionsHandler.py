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


from models import dbsession, User, GameLevel
from libs.Notifier import Notifier
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler


class MissionsHandler(BaseHandler):
    ''' Displays user password hashes '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Render missions view '''
        user = self.get_current_user()
        self.render("missions/view.html", team=user.team, errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Submit flags '''
        uri = {
            'flag': self.flag,
            'buyout': self.buyout,
        }

