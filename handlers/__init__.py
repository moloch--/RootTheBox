# -*- coding: utf-8 -*-

import logging
from os import urandom, path
from base64 import b64encode
from tornado.ioloop import IOLoop #@UnresolvedImport
from tornado.web import Application #@UnresolvedImport
from tornado.web import StaticFileHandler #@UnresolvedImport

from handlers.BoxHandlers import *
from handlers.RootHandlers import *
from handlers.UserHandlers import *
from handlers.AdminHandlers import *
from handlers.ErrorHandlers import *
from handlers.HashesHandlers import *
from handlers.CrackMeHandlers import *
from handlers.ReporterHandlers import *
from handlers.WebsocketHandlers import *
from handlers.ScoreboardHandlers import *
from handlers.PastebinHandlers import *

from models import dbsession
from modules.Menu import Menu
import models

def cache_actions():
    ''' Loads all of the actions from the database into memory for the scoreboard pages'''
    action_list = dbsession.query(models.Action).all()
    ws_manager = WebSocketManager.Instance()
    for action in action_list:
        team = dbsession.query(models.User).filter_by(id=action.user_id).first()
        score_update = ScoreUpdate(action.created.strftime("%d%H%M%S"), action.value, team.team_name, team.score)
        ws_manager.currentUpdates.append(score_update)
        
logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.DEBUG)

application = Application([
        # Static Handlers - Serves static CSS, JavaScript and image files
        (r'/static/(.*)', StaticFileHandler, {'path': 'static'}),
        (r'/avatars/(.*)', StaticFileHandler, {'path': 'files/avatars'}),
        
        # Reporter Handlers - Communication with reporters
        (r'/reporter/register', ReporterRegistrationHandler, {'dbsession': dbsession}),
        
        # User Handlers - Serves user related pages
        (r'/user/shares/download(.*)', ShareDownloadHandler, {'dbsession': dbsession}),
        (r'/user/shares', ShareUploadHandler, {'dbsession': dbsession}),
        (r'/user/settings(.*)', SettingsHandler, {'dbsession': dbsession}),
        (r'/user/logout', LogoutHandler, {'dbsession': dbsession}),
        (r'/user', HomeHandler, {'dbsession': dbsession}),
        
        # Box Handlers - Serves box related pages
        (r'/boxes(.*)', BoxesViewHandler, {'dbsession': dbsession}),
        
        # Crack Me Handlers - Serves crack me related pages
        (r'/crackme/download(.*)', CrackMeDownloadHandler, {'dbsession': dbsession}),
        (r'/crackme(.*)', CrackMeHandler, {'dbsession': dbsession}),
        
        # Hashes Handler - Serves hash related pages
        (r'/hashes(.*)', HashesHandler, {'dbsession': dbsession}),
        
        # Scoreboard Handlers - Severs scoreboard related pages
        (r'/scoreboard(.*)', ScoreBoardHandler, {'dbsession': dbsession}),
        
        # Admin Handlers - Administration pages
        (r'/admin/create/(.*)', AdminCreateHandler, {'dbsession':dbsession}),
        (r'/admin/edit/(.*)', AdminEditHandler, {'dbsession':dbsession}),
        (r'/admin/notify', AdminNotifyHandler),
        
        #Websocket Handlers - Websocket communication handlers
        (r'/websocket', WebsocketHandler),
        
        #Pastebin Handlers
        (r'/pastebin', PastebinHandler, {'dbsession':dbsession}),
        (r'/pastebin/view(.*)', DisplayPostHandler, {'dbsession':dbsession}),
        
        # Root handler - Serves all public pages
        (r'/login', LoginHandler),
        (r'/registration', UserRegistraionHandler, {'dbsession': dbsession}),
        (r'/about', AboutHandler),
        (r'/', WelcomeHandler),
        
        # Error handlers - Serves error pages
        (r'/403(.*)', UnauthorizedHandler),
        (r'/(.*).php', PhpHandler),
        (r'/(.*)', NotFoundHandler)
    ],
                          
    # Randomly generated secret key
    cookie_secret = b64encode(urandom(64)),
    
    # Ip addresses that access the admin interface
    admin_ips = ('127.0.0.1'),
    
    # Template directory
    template_path = 'templates',
    
    # Request that does not pass @authorized will be redirected here
    forbidden_url = '/403',
    
    # Requests that does not pass @authenticated  will be redirected here
    login_url = '/login',
    
    # UI Modules
    ui_modules = {"Menu": Menu},
    
    # Enable XSRF forms
    xsrf_cookies = True,
    
    # Special file directories
    avatar_dir = path.abspath('files/avatars/'),
    crack_me_dir = path.abspath('files/crack_mes/'),
    shares_dir = path.abspath('files/shares'),
    se_dir = path.abspath('files/se/'),

    # Seconds between scoring
    ticks = 120,

    # Debug mode
    debug = True,
    
    # Application version
    version = '0.1'
)

# the port. doh
application.listen(8888)

# calling this will start the IOLoop. open your browser and enjoy.
__serve__ = lambda: IOLoop.instance().start()

#cache the actions
cache_actions()

def start():
    scoring = ioloop.PeriodicCallback(self.scoring, self.ioLoop)
    sockets = tornado.netutil.bind_sockets(8888)
    tornado.process.fork_processes(-1)
    server = HTTPServer(application)
    server.add_sockets(sockets)
    
