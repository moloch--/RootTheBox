'''
Created on Mar 14, 2012

@author: moloch
'''

from libs.Session import SessionManager
from tornado.web import UIModule #@UnresolvedImport

class Menu(UIModule):
    
    def render(self, *args, **kwargs):
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.handler.get_secure_cookie('auth'), self.request.remote_ip)
        if session != None:
            if session.data['menu'] == 'user':
                return self.render_string('menu/user.html')
            elif session.data['menu'] == 'admin':
                return self.render_string('menu/admin.html')
        return self.render_string('menu/public.html')