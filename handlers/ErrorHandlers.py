'''
Created on Mar 13, 2012

@author: moloch
'''

from tornado.web import RequestHandler #@UnresolvedImport

class NotFoundHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the 404 page '''
        self.render("public/404.html")
        
class UnauthorizedHandler(RequestHandler):
    
    def get(self, *args, **kwargs):
        ''' Renders the 403 page '''
        self.render("public/403.html")
        
class PhpHandler(RequestHandler):
    
    def get(self, *args, **kwargs):
        ''' Renders the php page '''
        self.render("public/php.html")