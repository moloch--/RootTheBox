# -*- coding: utf-8 -*-
"""
tests the RootController
"""

from tests import ApplicationTest

class RootTest(ApplicationTest):
    def test(self): pass
    
    def test_index(self):
        # checks out the '/' path
        self.get('/')(self.stop)
        rsp = self.wait()
        assert 'hello' in rsp.body
    
    def test_users_only_unauth(self):
        # should redirect to '/login' page cause there is no authed user
        self.get('/users_only')(self.stop)
        rsp = self.wait()
        assert '/login' in rsp.effective_url
    
    def test_users_only_auth(self):
        # check out how I passed the auth=(user, password)
        self.get('/users_only', auth=('user', 'user'))(self.stop)
        rsp = self.wait()
        assert 'secret' in rsp.body
        
    def test_admins_only_user(self):
        # should redirect to '/forbidden' page
        self.get('/admins_only', auth=('user', 'user'))(self.stop)
        rsp = self.wait()
        assert '/forbidden' in rsp.effective_url
        
    def test_admins_only_admin(self):
        # allas is good!
        self.get('/admins_only', auth=('admin', 'admin'))(self.stop)
        rsp = self.wait()
        assert 'welcome' in rsp.body