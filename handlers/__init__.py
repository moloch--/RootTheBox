# -*- coding: utf-8 -*-
"""
this sets up the tornado application  and handlers.
for more information about tornado check out <a href="http://www.tornadoweb.org">www.tornadoweb.org</a>
"""
import logging
from os import urandom
from hashlib import sha512
from tornado.ioloop import IOLoop #@UnresolvedImport
from tornado.web import Application #@UnresolvedImport

# import your handlers and set the application routes and configuration
from handlers.root import RootController

logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.DEBUG)

secretHash = sha512
secretHash.update(urandom(512))
secret = secretHash.hexdigest()

application = Application([
        # the RootController also serve as a StaticFileHandler. 'path' is mandatory, 'default_filename' is optional
        (r'/(.*)', RootController, {'path': 'public', 
                                    'default_filename': 'index.html'})
    ],
    cookie_secret="Dkj50&Xl!QVKZ*!tu^pBk7f1AJ6zJ@#6Dkj50&Xl!QVKZ*!tu^pBk7f1AJ6zJ@#6",
    template_path='templates',
    # request that does not pass @authorized will be redirected here
    forbidden_url='/forbidden',
    # requests that does not pass @authenticated  will be redirected here
    login_url='/login',
    # integer, in minutes, for how long until the session expires
    session_expire=20,
    # debug mode uses torando.autoreload module to reload the app on modules/templates
    # change and print out errors as response. delete or set to False for production
    debug=True
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