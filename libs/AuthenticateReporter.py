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
from models import dbsession, Action
from libs.WebSocketManager import WebSocketManager

TIMEOUT = 1
XID_SIZE = 24
BUFFER_SIZE = 1024

def scoring_round():
    ''' Multi-threaded scoring '''
    boxes = list(Box.get_all())
    logging.info("Starting scoring round with %d boxes" % len(boxes))
    for box in boxes:
        score_box(box)
    logging.info("Scoring round completed")

def score_box(box):
    ''' Scores a single box '''
    logging.info("Scoring reporters on %s" % (box.box_name,))
    threads = []
    for user in box.users:
        thread = threading.Thread(target = score_user, args = (box, user))
        threads.append(thread)
        thread.start()
        for thread in threads:
            thread.join(timeout = TIMEOUT)

def score_user(box, user):
    ''' Scores a single user/team '''
    auth = AuthenticateReporter(box, user)
    auth.check_validity()
    if auth.confirmed_access != None:
        award_points(box, user, auth)
    else:
        user.lost_control(box)
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

class AuthenticateReporter():

    def __init__(self, box, user):
        self.sha = sha256()
        self.box = box
        self.port = user.team.listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.confirmed_access = None
        self.pending_access = None
    
    def check_validity(self):
        ''' Checks the validity of a reporter on a box '''
        logging.info("Checking for reporter at %s:%s" % (self.box.ip_address, self.port))
        try:
            self.sock.connect((self.box.ip_address, self.port))
            self.pending_access = self.sock.recv(BUFFER_SIZE)
            if self.pending_access == 'root':
                    self.sha.update(self.box.root_key)
                    self.verify_response()
            elif self.pending_access == 'user':
                    self.sha.update(self.box.user_key)
                    self.verify_response()
            else:
                    logging.info("Reporter provided an invalid access level")
        except:
            logging.info("Failed to connect to reporter")

    def verify_response(self):
        ''' Verifies zero-knowledge proof '''
        self.send_xid()
        response = self.sock.recv(BUFFER_SIZE)
        if response == self.sha.hexdigest():
            self.confirmed_access = bool(self.pending_access == 'root')
        else:
            logging.info("Reporter's response was invalid")

    def send_xid(self):
        ''' Sends transaction id to client '''
        xid = b64encode(urandom(XID_SIZE))
        self.sock.sendall(xid)
        self.sha.update(xid)
