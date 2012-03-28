# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch
'''

import models
import logging

from time import sleep
from os import urandom, path
from base64 import b64encode
from models import dbsession
from modules.Menu import Menu
from libs.Session import SessionManager
from libs.HostIpAddress import HostIpAddress
from libs.AuthenticateReporter import scoring_round
from tornado import netutil
from tornado import process
from tornado.web import Application
from tornado.web import StaticFileHandler 
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from handlers.BoxHandlers import *
from handlers.RootHandlers import *
from handlers.UserHandlers import *
from handlers.AdminHandlers import *
from handlers.ErrorHandlers import *
from handlers.HashesHandlers import *
from handlers.SocialHandlers import *
from handlers.CrackMeHandlers import *
from handlers.ReporterHandlers import *
from handlers.PastebinHandlers import *
from handlers.PastebinHandlers import *
from handlers.WebsocketHandlers import *
from handlers.ScoreboardHandlers import *
       
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
        (r'/user/team', TeamViewHandler, {'dbsession': dbsession}),
        (r'/user/logout', LogoutHandler, {'dbsession': dbsession}),
        (r'/user/reporter', ReporterHandler, {'dbsession': dbsession}),
        (r'/user', HomeHandler, {'dbsession': dbsession}),
        
        # Box Handlers - Serves box related pages
        (r'/boxes(.*)', BoxesViewHandler, {'dbsession': dbsession}),
        
        # Crack Me Handlers - Serves crack me related pages
        (r'/crackme/download(.*)', CrackMeDownloadHandler, {'dbsession': dbsession}),
        (r'/crackme(.*)', CrackMeHandler, {'dbsession': dbsession}),
        
        # Hashes Handlers - Serves hash related pages
        (r'/hashes(.*)', HashesHandler, {'dbsession': dbsession}),
        (r'/wallofsheep', WallOfSheepHandler, {'dbsession': dbsession}),
        
        # Scoreboard Handlers - Severs scoreboard related pages
        (r'/scoreboard(.*)', ScoreBoardHandler, {'dbsession': dbsession}),
        
        # Challenges Handlers
        (r'/challenge(.*)', ChallengeHandler, {'dbsession' : dbsession}),
        
        # Social Challenges Handlers
        (r'/se(.*)', SocialHomeHandler, {'dbsession':dbsession}),
        
        # Admin Handlers - Administration pages
        (r'/admin/create/(.*)', AdminCreateHandler, {'dbsession':dbsession}),
        (r'/admin/edit/(.*)', AdminEditHandler, {'dbsession':dbsession}),
        (r'/admin/notify', AdminNotifyHandler),
        
        #Websocket Handlers - Websocket communication handlers
        (r'/websocket', WebsocketHandler),
        
        #Pastebin Handlers
        (r'/pastebin', PastebinHandler, {'dbsession':dbsession}),
        (r'/pastebin/view(.*)', DisplayPostHandler, {'dbsession':dbsession}),
        (r'/pastebin/delete(.*)', DeletePostHandler, {'dbsession':dbsession}),
        
        # Root handlers - Serves all public pages
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
    
    # Recaptcha Key
    recaptcha_private_key = "6LcJJ88SAAAAAPPAN72hppldxema3LI7fkw0jaIa",

    # WebSocket Host IP Address
    ws_ip_address = HostIpAddress().get_ip_address(),

    # Special file directories
    avatar_dir = path.abspath('files/avatars/'),
    crack_me_dir = path.abspath('files/crack_mes/'),
    shares_dir = path.abspath('files/shares/'),
    se_dir = path.abspath('files/se/'),

    # Milli-Seconds between scoring
    ticks = int(30 * 1000),

    # Milli-Seconds between session clean up
    clean_up_timeout = int(120 * 1000),

    # Debug mode
    debug = False,
    
    # Application version
    version = '0.1'
)
def cache_actions():
    ''' Loads all of the actions from the database into memory for the scoreboard pages'''
    action_list = dbsession.query(models.Action).all()
    ws_manager = WebSocketManager.Instance()
    for action in action_list:
        team = dbsession.query(models.User).filter_by(id=action.user_id).first()
        score_update = ScoreUpdate(action.created.strftime("%d%H%M%S"), action.value, team.team_name)
        ws_manager.currentUpdates.append(score_update)
 
# Start the server
def start_game():
    ''' Main entry point for the application '''
    cache_actions()
    sockets = netutil.bind_sockets(8888)
    if process.task_id() == None:
        tornado.process.fork_processes(-1, max_restarts = 10)
    server = HTTPServer(application)
    server.add_sockets(sockets)
    io_loop = IOLoop.instance()
    session_manager = SessionManager.Instance()
    if process.task_id() == 1:
        scoring = PeriodicCallback(scoring_round, application.settings['ticks'], io_loop = io_loop)
        session_clean_up = PeriodicCallback(session_manager.clean_up, application.settings['clean_up_timeout'], io_loop = io_loop)
        scoring.start()
        session_clean_up.start()
    try:
        io_loop.start()
    except KeyboardInterrupt:
        if process.task_id() == 1:
            print '\r[!] Shutdown Everything!'
            session_clean_up.stop()
            io_loop.stop()
