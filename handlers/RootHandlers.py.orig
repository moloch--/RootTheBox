'''
Created on Mar 13, 2012

@author: moloch
'''
import logging

from json import dumps
from models.User import User
from tornado.web import RequestHandler #@UnresolvedImport

class LoginHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render('public/login.html', header='User authentication required')
    
    def post(self, *args, **kwargs):
        ''' Checks submitted user_name and password '''
        try:
            user_name = self.get_argument('username')
            user = User.by_user_name(user_name)
        except:
            self.render('public/login.html', header="Type in an account name")
        
        try:
            password = self.get_argument('password')
        except:
<<<<<<< Updated upstream
            self.render('public/login.html', header="Type in a password")
        if user.validate_password(password):
=======
            self.render('login.html', header="Type in a password")

        if user != None and user.validate_password(password):
>>>>>>> Stashed changes
            logging.info("Successful login: %s" % user.user_name)
            self.set_secure_cookie('auth', dumps({
                    'id': user.id,
                    'name': user.display_name,
                })
            )
            self.redirect('/user')
        else:
<<<<<<< Updated upstream
            self.render('public/login.html', header="Failed login attempt, try again")
    
    def hashPassword(self, preimage):
        inputHash = md5()
        inputHash.update(preimage)
        return unicode(inputHash.hexdigest())
=======
            logging.info("failed login")
            self.render('login.html', header="Failed login attempt, try again")
>>>>>>> Stashed changes

class UserRegistraionHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render("public/registration.html", errors='Please fill out the form below')
    
    def post(self, *args, **kwargs):
        ''' Attempts to create an account '''
        # Check user_name parameter
        try:
            user_name = self.get_argument('username')
        except:
            self.render('public/registration.html', errors='Please enter a valid account name')
            
        # Check handle parameter
        try:
            handle = self.get_argument('handle')
        except:
            self.render('public/registration.html', errors='Please enter a valid handle')
        
        # Check password parameter
        try:
            password1 = self.get_argument('pass1')
            password2 = self.get_argument('pass2')
            if password1 != password2:
                self.render('public/registration.html', errors='Passwords did not match')
            else:
                password = password1
        except:
            self.render('registration.html', errors='Please enter a password')
        
        # Create account
        if User.by_user_name(user_name) != None:
            self.render('public/registration.html', errors='Account name already taken')
        elif User.by_display_name(handle) != None:
            self.render('public/registration.html', errors='Handle already taken')
        elif not 0 < len(password) <= 7:
            self.render('public/registration.html', errors='Password must be 1-7 characters')
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
