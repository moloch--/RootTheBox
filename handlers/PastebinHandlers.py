'''
Created on Mar 18, 2012

@author: haddaway
'''
from models import User, Post
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler #@UnresolvedImport
import logging

class PastebinHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        user = User.by_user_name(session.data['user_name'])
        if user.team != None:
            self.render('pastebin/view.html', posts = user.team.get_posts)
        else:
            self.render('pastebin/view.html', posts = [])
    @authenticated
    def post(self, *args, **kwargs):
        try:
            content = self.get_argument("content")
            new_name = self.get_argument("name")
        except:
            self.render('pastebin/error.html', errors="Please Enter something!")
        
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        user = User.by_user_name(session.data['user_name'])
        post = Post(
            name = new_name,
            contents = content,
            user_id = user.id)
        user.posts.append(post)
        self.dbsession.add(user)
        self.dbsession.flush()
        self.redirect('/pastebin')
        
class DisplayPostHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        user = User.by_user_name(session.data['user_name'])
        try:
            post_id = self.get_arguments("post_id")[0]
        except:
            self.render('pastebin/error.html', errors = "Invalid post id!")
            
        if user.team != None:
            logging.info(post_id)
            posts = user.team.get_posts
            post = self.dbsession.query(Post).filter_by(id=post_id).first()
            #if(post in posts):
            self.render('pastebin/display.html', contents = post.contents)
        else:
            self.render('pastebin/view.html', posts = [])
        