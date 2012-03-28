'''
Root the Box - Authenticate Reporter
Created on Feb 28, 2012

@author: moloch
'''

import time
import socket
import logging
import threading

from os import urandom
from models import Box
from hashlib import sha256
from base64 import b64encode
from tornado import iostream
from models import dbsession
from libs.WebSocketManager import WebSocketManager

TIMEOUT = 1
BUFFER_SIZE = 1024

def score_box(box):
    ''' Scores a single box '''
    logging.info("Starting a scoring round, good hunting!")
    for user in box.users:
        auth = AuthenticateReporter(box, user)
        auth.check_validity()
        if auth.confirmed_access != None:
            award_points(box, user, auth)
        else:
            user.lost_control(box.box_name)
            dbsession.add(user)
            dbsession.flush()

def award_points(box, user, auth):
    ''' Creates action based on pwnage '''
    if auth.confirmed_access:
        value = box.root_value
        description = "%s got root access on %s" % (user.display_name, box.box_name)
    else:
        value = box.user_value
        description = "%s got user level access on %s" % (user.display_name, box.box_name)
    action = Action(
        classification = unicode("Box Pwnage"),
        description = unicode(description),
        value = value,
        user_id = user.id
    )
    user.dirty = True
    dbsession.add(action)
    dbsession.add(user)
    dbsession.flush()
    ws_manager = WebSocketManager.Instance()
    avatar_path = self.application.settings['avatar_dir']+'/'+user.avatar
    notify = Notification("Box Pwnage", description, file_location = avatar_path)
    ws_manager.send_all(notify)

def scoring_round():
    ''' Multi-threaded scoring '''
    boxes = list(Box.get_all())
    threads = []
    logging.info("Starting scoring round with %d boxes" % len(boxes))
    for box in boxes:
        thread = threading.Thread(target = score_box, args = (box,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    logging.info("Scoring round completed")

class AuthenticateReporter():

    def __init__(self, box, user):
        self.sha = sha256()
        self.box = box
        self.port = user.team.listen_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        self.tcp_stream = iostream.IOStream(sock, max_buffer_size = BUFFER_SIZE)
        self.tcp_stream.set_close_callback(self.set_done)
        self.tcp_stream.connect((self.box.ip_address, self.port))
        self.confirmed_access = None
        self.pending_access = None
        self.done = False
    
    def set_done(self):
        ''' Set flag when authentication protocol has completed '''
        self.done = True
    
    def check_validity(self):
        ''' Checks the validity of a reporter on a box '''
        logging.info("Checking for reporter at %s:%s" % (self.box.ip_address, self.port))
        try:
            self.tcp_stream.read_bytes(len('root'), self.check_access_level)
            time.sleep(TIMEOUT)
            if not self.done:
                logging.info("A reporter stopped responding on %s" % self.box.ip_address)
                self.kill()
        except socket.error, error:
            logging.info("Failed to connect to host %s: %s" % (self.box.ip_address, error))
            self.set_done()

    def check_access_level(self, pending_access):
        ''' Check if the reporter provided a valid access level '''
        self.pending_access = pending_access
        if self.pending_access == 'root':
            self.sha.update(self.box.root_key)
            self.send_xid()
        elif self.pending_access == 'user':
            self.sha.update(self.box.user_key)
            self.send_xid()
        else:
            logging.info("A reporter submitted an invalid access level")
            self.tcp_stream.write("Error - Invalid access level %s" % self.pending_access)
            self.tcp_stream.close()

    def send_xid(self):
        ''' Send the reporter the transaction id '''
        xid = self.get_xid()
        self.tcp_stream.write(xid)
        self.sha.update(xid)
        while self.tcp_stream.writing():
            time.sleep(0.01)
        self.tcp_stream.read_bytes(len(self.sha.hexdigest()), self.check_response)
            
    def check_response(self, response):
        ''' Checks if the reporter provided a valid response '''
        if self.sha.hexdigest() == response:
            self.tcp_stream.write("Success")
            self.confirmed_access = (self.pending_access == 'root')
            self.tcp_stream.close()
        else:
            logging.info("A reporter submitted an invalid sha value")
            self.tcp_stream.write("Error - Checksum mismatch")
            self.tcp_stream.close()

    def get_xid(self):
        ''' Returns a randomly generated transaction id '''
        return b64encode(urandom(24))

    def kill(self):
        ''' Kills the connection to the reporter regardless of state '''
        self.tcp_stream.close()
