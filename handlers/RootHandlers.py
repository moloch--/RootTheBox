'''
Created on Mar 13, 2012

@author: moloch
'''
import logging

from hashlib import md5
from models.User import User
from tornado.web import RequestHandler #@UnresolvedImport
from tornado.web import asynchronous #@UnresolvedImport

class LoginHandler(RequestHandler):

    @asynchronous
    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render('login.html', header='User authentication required')
    
    @asynchronous
    def post(self, *args, **kwargs):
        ''' Checks submitted user_name and password '''
        user_name = self.get_argument('username')
        user = User.by_user_name(user_name)
        password = self.get_argument('password')
        if user != None and user.password == self.hashPassword(password):
            logging.info("Successful login: %s" % user.user_name)
            self.redirect('/user')
        else:
            self.render('login.html', header="Failed login attempt, try again")
    
    def hashPassword(self, preimage):
        inputHash = md5()
        inputHash.update(preimage)
        return unicode(inputHash.hexdigest())

class UserRegistraionHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @asynchronous
    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render("registration.html", errors='Please fill out the form below')
    
    @asynchronous
    def post(self, *args, **kwargs):
        ''' Attempts to create an account '''
        # Check user_name parameter
        try:
            user_name = self.get_argument('username')
        except:
            self.render('registration.html', errors='Please enter a valid account name')
            
        # Check handle parameter
        try:
            handle = self.get_argument('handle')
        except:
            self.render('registration.html', errors='Please enter a valid handle')
        
        # Check password parameter
        try:
            password1 = self.get_argument('pass1')
            password2 = self.get_argument('pass2')
            if password1 != password2:
                self.render('registration.html', errors='Passwords did not match')
            else:
                password = password1
        except:
            self.render('registration.html', errors='Please enter a password')
        
        # Create account
        if User.by_user_name(user_name) != None:
            self.render('registration.html', errors='Account name already taken')
        elif User.by_display_name(handle) != None:
            self.render('registration.html', errors='Handle already taken')
        elif not 0 < len(password) <= 7:
            self.render('registration.html', errors='Password must be 1-7 characters')
        else:
            user = User(
                user_name = user_name,
                display_name = handle,
                password = password
            )
            self.dbsession.add(user)
            self.dbsession.flush()
            self.redirect('/login')
    
class AboutHandler(RequestHandler):

    @asynchronous
    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('about.html')
        

class WelcomeHandler(RequestHandler):

    @asynchronous
    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('welcome.html')