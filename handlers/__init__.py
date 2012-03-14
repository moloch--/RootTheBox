# -*- coding: utf-8 -*-
"""
this sets up the tornado application  and handlers.
for more information about tornado check out <a href="http://www.tornadoweb.org">www.tornadoweb.org</a>
"""
import logging
from os import urandom
from base64 import b64encode
from tornado.ioloop import IOLoop #@UnresolvedImport
from tornado.web import Application #@UnresolvedImport
from tornado.web import StaticFileHandler #@UnresolvedImport

# import your handlers and set the application routes and configuration
from handlers.BoxHandlers import *
from handlers.RootHandlers import *
from handlers.UserHandlers import *
from handlers.ErrorHandlers import *
from handlers.ReporterHandlers import *
from models import dbsession

logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.DEBUG)

application = Application([
        # Static Handler - Serves static CSS, JavaScript and image files
        (r'/static/(.*)', StaticFileHandler, {'path': 'static'}),
        
        # Reporter Handlers - Communication with reporters
        (r'/reporter/register', ReporterRegistrationHandler, {'dbsession': dbsession}),
        
        # User Handlers - Serves user related pages
        (r'/user/settings(.*)', SettingsHandler, {'dbsession': dbsession}),
        (r'/user/logout(.*)', LogoutHandler),
        (r'/user(.*)', HomeHandler, {'dbsession': dbsession}),
        
        # Box Handlers - Serves box related pages
        (r'/boxes(.*)', BoxesViewHandler, {'dbsession': dbsession}),
        
        # Scoreboard Handlers - Severs scoreboard related pages
        #(r'/scoreboard(.*)'
        
        # Admin Handlers - Administration pages
        #r('/admin/create_boxes(.*)
<<<<<<< Updated upstream
        #r('/admin/users(.*)
        #r('/admin/create_teams(.*)
        #r('/admin(.*)', 
=======
        #r('/admin/create_users(.*)
        #r('/admin/create_teams(.*)
        #r('/admin(.*)
>>>>>>> Stashed changes
        
        # Root handler - Serves all public pages
        (r'/login(.*)', LoginHandler),
        (r'/registration(.*)', UserRegistraionHandler, {'dbsession': dbsession}),
        (r'/about(.*)', AboutHandler),
        (r'/', WelcomeHandler),
        
        # Error handlers - Serves error pages
        (r'/403(.*)', UnauthorizedHandler),
        (r'/(.*)', NotFoundHandler)
    ],
    cookie_secret = b64encode(urandom(64)),
    template_path ='templates',
    
    # request that does not pass @authorized will be redirected here
    forbidden_url ='/403',
    
    # requests that does not pass @authenticated  will be redirected here
    login_url = '/login',
    
    # integer, in minutes, for how long until the session expires
    session_expire = 20,
    # debug mode uses torando.autoreload module to reload the app on modules/templates
    # change and print out errors as response. delete or set to False for production
    debug = True,
    version = '0.1'
)
# the port. doh
application.listen(8888)

# calling this will start the IOLoop. open your browser and enjoy.
__serve__ = lambda: IOLoop.instance().start()


#def start():
#    sockets = tornado.netutil.bind_sockets(8888)
#    tornado.process.fork_processes(-1)
#    server = HTTPServer(application)
#    server.add_sockets(sockets)