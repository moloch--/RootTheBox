'''
Created on Mar 13, 2012

@author: moloch
'''
import logging

from models.User import User
from libs.Session import SessionManager
from tornado.web import RequestHandler #@UnresolvedImport
from recaptcha.client import captcha
from libs import Config

class LoginHandler(RequestHandler):

    def initialize(self):
        self.config = Config.Config()

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render('public/login.html', header = 'User authentication required')
    
    def post(self, *args, **kwargs):
        ''' Checks submitted user_name and password '''
        logging.info(self.request.arguments)
        try:
            user_name = self.get_argument('username')
            user = User.by_user_name(user_name)
        except:
            self.render('public/login.html', header = "Type in an account name")
        
        try:
            password = self.get_argument('password')
        except:
            self.render('public/login.html', header = "Type in a password")

        try:
            response = captcha.submit(
                self.get_argument('recaptcha_challenge_field'),
                self.get_argument('recaptcha_response_field'),
                self.config.recaptcha_private_key,
                self.request.remote_ip,)
        except:
            self.render('public/login.html', header = "Please fill out recaptcha!")

        if user != None and user.validate_password(password) and response.is_valid:
            logging.info("Successful login: %s from %s" % (user.user_name, self.request.remote_ip))
            session_manager = SessionManager.Instance()
            sid, session = session_manager.start_session()
            self.set_secure_cookie(name = 'auth', value = str(sid), expires_days = 1, HttpOnly=True)
            session.data['user_name'] = str(user.user_name)
            session.data['ip'] = str(self.request.remote_ip)
            if user.has_permission('admin'):
                session.data['menu'] = str('admin')
            else:
                session.data['menu'] = str('user')
            self.redirect('/user')
        else:
            logging.info("Failed login attempt from %s " % self.request.remote_ip)
            self.render('public/login.html', header = "Failed login attempt, try again")

class UserRegistraionHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.config = Config.Config()
    
    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render("public/registration.html", errors = 'Please fill out the form below')
    
    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        # Check user_name parameter
        try:
            user_name = self.get_argument('username')
        except:
            self.render('public/registration.html', errors = 'Please enter a valid account name')
            
        # Check handle parameter
        try:
            handle = self.get_argument('handle')
        except:
            self.render('public/registration.html', errors = 'Please enter a valid handle')
        
        # Check password parameter
        try:
            password1 = self.get_argument('pass1')
            password2 = self.get_argument('pass2')
            if password1 != password2:
                self.render('public/registration.html', errors = 'Passwords did not match')
            else:
                password = password1
        except:
            self.render('public/registration.html', errors = 'Please enter a password')
        
        #Check recaptcha
        try:
            response = captcha.submit(
                self.get_argument('recaptcha_challenge_field'),
                self.get_argument('recaptcha_response_field'),
                self.config.recaptcha_private_key,
                self.request.remote_ip,)
        except:
            self.render('public/registration.html', errors = "Please fill out recaptcha!")

        
        # Create account
        if User.by_user_name(user_name) != None:
            self.render('public/registration.html', errors = 'Account name already taken')
        elif User.by_display_name(handle) != None:
            self.render('public/registration.html', errors = 'Handle already taken')
        elif not 0 < len(password) <= 7:
            self.render('public/registration.html', errors = 'Password must be 1-7 characters')
        elif not response.is_valid:
            self.render('public/registration.html', errors = 'Invalid Recaptcha!')
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

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('public/about.html')
        
class WelcomeHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/welcome.html")
