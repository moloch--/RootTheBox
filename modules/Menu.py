'''
Created on Mar 14, 2012

@author: moloch
'''

from libs import sessions
from tornado.web import UIModule #@UnresolvedImport

class Menu(UIModule):
    
    def render(self, *args, **kwargs):
        sid = self.handler.get_secure_cookie('auth')
        if sid != None and sessions.has_key(sid):
            session = sessions[sid]
            if not session.is_expired():
                if session.data['menu'] == 'user':
                    return self.render_string('menu/user.html')
                elif session.data['menu'] == 'admin':
                    return self.render_string('menu/admin.html')
            else:
                del sessions[sid]
        return self.render_string('menu/public.html')