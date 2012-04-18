'''
Created on Mar 18, 2012

@author: haddaway

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
            self.render('pastebin/view.html', posts = user.team.posts)
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
            post_id = self.get_argument("post_id")
        except:
            self.render('pastebin/error.html', errors = "Invalid post id!")
            
        if user.team != None:
            posts = user.team.posts
            post = self.dbsession.query(Post).filter_by(id=post_id).first()
            if(post in posts):
                self.render('pastebin/display.html', contents = post.contents, name=post.name)
            else:
                self.render('pastebin/error.html', errors = "Invalid Post Id!")
        else:
            self.render('pastebin/view.html', posts = [])
            
class DeletePostHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    @authenticated
    def get(self, *args, **kwargs):
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        user = User.by_user_name(session.data['user_name'])
        try:
            post_id = self.get_argument("post_id")
        except:
            self.render('pastebin/error.html', errors = "Invalid post id!")
            
        if user.team != None:
            posts = user.team.posts
            post = self.dbsession.query(Post).filter_by(id=post_id).first()
            if(post in posts):
                self.dbsession.delete(post)
                self.dbsession.flush()
                posts = user.team.posts
            self.redirect('/pastebin')
        else:
            self.render('pastebin/view.html', posts = [])