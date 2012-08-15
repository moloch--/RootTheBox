'''
Created on Mar 14, 2012

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


from libs.Session import SessionManager
from tornado.web import UIModule
from models import User


class Menu(UIModule):

    def render(self, *args, **kwargs):
        ''' Renders the top menu '''
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(
            self.handler.get_secure_cookie('auth'), self.request.remote_ip)
        if session != None:
            if session.data['menu'] == 'user':
                user = User.by_handle(session.data['handle'])
                return self.render_string('menu/user.html', handle=user.handle, team_name=user.team.name)
            elif session.data['menu'] == 'admin':
                return self.render_string('menu/admin.html', handle="Admin")
        return self.render_string('menu/public.html')
