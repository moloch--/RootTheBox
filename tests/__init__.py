# -*- coding: utf-8 -*-
"""
defines a special ApplicationTest class.
inheriate it inorder to write tests for the application
"""

from handlers import application
from libs.form_xcode import form_encode
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase

# ApplicationTest
# ---------------
class ApplicationTest(AsyncHTTPTestCase):
    get_app = lambda self: application
    
    # defines a self.get/post that will ease writing tests for the app.
    # also, checkout the tests em'self in tests/root.py
    # and tornado.testing to see how the heck async testing works.
    
    get = lambda self, path, **kw: self.__fetch(path, method='GET', **kw)
    post = lambda self, path, **kw: self.__fetch(path, method='POST', **kw)
    def __fetch(self, path, **kw):
        # setting body or query string
        data = kw.get('data', '')
        if data:
            kw.pop('data')
            data = form_encode(data)

        method = kw['method']
        if method == 'GET': path = '%s?%s'%(path, data)
        elif method == 'POST': kw['body'] = data
        
        # getting auth cookie and setting it for the request
        auth = kw.get('auth')
        if auth:
            kw.pop('auth')

            try:
                # posting to /login in order to get the auth cookie. if login fails, treats as unauthed
                self.post('/login', data={'user_name': auth[0], 'password': auth[1]}, follow_redirects=False)(self.stop)
                auth_cookie = '%s;'%self.wait().headers['Set-Cookie'].split(';')[0]

                headers = kw.get('headers', {})
                headers['Cookie'] = auth_cookie + headers.get('Cookie', '')
                kw['headers'] = headers
            except:
                pass
    
        return lambda callback: self.http_client.fetch(HTTPRequest(self.get_url(path), **kw), callback)

# import your tests here!
from tests.root import RootTest