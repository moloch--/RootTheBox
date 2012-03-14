'''
Created on Mar 13, 2012

@author: moloch
'''

from tornado.web import RequestHandler #@UnresolvedImport

class NotFoundHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the 404 page '''
        self.render("404.html")
        
class UnauthorizedHandler(RequestHandler):
    
    def get(self, *args, **kwargs):
        ''' Renders the 403 page '''
        self.render("403.html")