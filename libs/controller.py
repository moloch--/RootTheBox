# -*- coding: utf-8 -*-
"""
a special class called ControllerHandler
which ease the way of writing a BaseHandler,
BaseHandler is a regular tornado's RequestHandler with methods
that integrates with the the app's forbidden_url/@authorized,
and request's current_session/current_user
"""

from json import loads
from random import random
from functools import wraps
from urllib import urlencode
from urlparse import urlsplit
from models import dbsession, User
from libs.form_xcode import form_decode
from datetime import datetime, timedelta
from tornado.web import HTTPError, RequestHandler, StaticFileHandler #@UnresolvedImport

def authorized(permission):
    """
    @authorized
    -----------
    Decorate methods with this to require that the user must have the required permission.
    used @tornado.web.authenticated as inspiration
    """
    def func(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user.has_permission(permission):
                if self.request.method in ('GET', 'HEAD'):
                    url = self.get_forbidden_url()
                    if '?' not in url:
                        # if forbidden url is absolute, make next absolute too
                        if urlsplit(url).scheme: next_url = self.request.full_url()
                        else: next_url = self.request.uri
                        url += '?' + urlencode(dict(next=next_url))
                    self.redirect(url)
                    return
                raise HTTPError(403)
            return method(self, *args, **kwargs)
        return wrapper
    return func

# __some unbound methods for BaseHandler__

# this holds the sessions for the controllers and handlers
sessions = {}

def get_current_session(self):
    """
    Return the request's session object.
    can be called using BaseHandler self.get_current_session() or
    by get_current_session(request_handler_instance)    
    """
    # loads the session if have a session cookie and have a session key in sessions. else None
    session = sessions.get(self.get_cookie('session'))
    
    # creats a new session incase there isn't one or if requested session expired
    if not session or session['expires'] < datetime.now():
        id = str(abs(hash(random()))) #@ReservedAssignment
        self.set_cookie('session', id)
        sessions[id] = session = {'data': {}}
    # prolongs session expire time with session_expire or the default 20 minutes
    session['expires'] = datetime.now() + timedelta(minutes=self.application.settings.get('session_expire', 20))
    return session['data']
        
def get_current_user(self):
    """
    Return the request's user object.
    can be called using BaseHandler self.get_current_user() or
    by get_current_user(request_handler_instance)    
    """
    # loads the cookie and query the database to compare passwords.
    # if password was changed/deleted (in the server side) then treats as unauthed
    auth = loads(self.get_secure_cookie('auth') or '""')
    if auth:
        user = dbsession.query(User).get(auth['id']) #@UndefinedVariable
        if user and user.password[0:8] == auth['password']: return user

# BaseHandler
# -----------
# just your ordinary RequestHandler, as you love and know it.
class BaseHandler(RequestHandler):
    def get_forbidden_url(self):
        """
        Override to customize the forbidden URL based on the request.
        By default, we use the 'forbidden_url' application setting.
        used ReuqestHandler.get_login_url as inspiration
        """
        self.require_setting('forbidden_url', '@libs.controller.authorized')
        return self.application.settings['forbidden_url']
        
    @property
    def current_session(self):
        if not hasattr(self, '_current_session'): self._current_session = self.get_current_session()
        return self._current_session
    
    # patching the class.
    get_current_session = get_current_session
    get_current_user = get_current_user

# __some unbound methods for ControllerHandler__

# this is a 404 for function not found.
call_func_error = HTTPError(404, 'Function')

# this is a BaseHandler to ControllerHandler, uri to function translation, check ControllerHandler
def call_func(self, uri, error=call_func_error):
    # try to get the function and arguments
    method = self.request.method.lower()
    uri = ('%s/'%uri.strip('/')).split('/')
    [func, self.args] = [getattr(self, '_%s_%s'%(method, uri[0]), None), uri[1:-1]]
    
    if not func:
        # if function not found, assumes it's the '\_method_' (e.g. '\_get_', '\_post_') function
        # and entire uri as arguments, trying to get that function
        [func, self.args] = [getattr(self, '_%s_'%method, None), uri[0:-1]]
        # raise the 404 error if '\_method_' function was not found.
        if not func: 
            raise error
        
    # decodes the query string / form body
    self.kw = form_decode('&'.join([self.request.uri.partition('?')[2], self.request.body]))
    # calls the function. if arguments cause TypeError will raise 500 error
    func(*self.args, **self.kw)

# ControllerHandler
# -----------------
class ControllerHandler(BaseHandler):
    # this will route all the requests to the call_func method, that will call the method on the controller
    get = post = put = delete = head = options = call_func

# RootControllerHandler
# --------------------
# same as ControllerHandler, just integrated into StaticFileHandler
class RootControllerHandler(StaticFileHandler, BaseHandler):
    post = put = delete = options = call_func
    initialize = lambda self, **kw: super(RootControllerHandler, self).initialize(kw['path'], default_filename=kw.get('default_filename'))
    def get(self, path, include_body=True):
        """
        overrode the GET method specifically (browsers request files using GET).
        files win methods, hence, a file named /my_data will be served
        even if there is a method by this name. avoid such things.
        """
        try: 
            super(RootControllerHandler, self).get(path, include_body=include_body)
        except HTTPError as error: 
            call_func(self, path, error=error)
        
        
