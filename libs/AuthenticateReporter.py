# -*- coding: utf-8 -*-

'''
Root the Box - Authenticate Reporter
Created on Feb 28, 2012

@author: moloch

    Copyright 2012 Root the Box

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


import time
import socket
import logging
import threading


from os import urandom
from hashlib import sha256
from base64 import b64encode
from models import dbsession, Team, Box
from libs.Notifier import Notifier


### Scoring Configuration ###
TIMEOUT = 1
XID_SIZE = 24
BUFFER_SIZE = 1024


def scoring_round():
    ''' 
    Executed as a periodic callback for main io_loop: Iterates of all the boxes
    and scores each box.
    '''
    boxes = list(Box.all())
    logging.info("Starting scoring round with %d boxes" % len(boxes))
    for box in boxes:
        score_box(box)
    logging.info("Scoring round completed")


def score_box(box):
    ''' 
    Spawns threads for each team, each thread attempts to authenticate it's team
    using the team's listen_port.
    '''
    logging.info("Scoring reporters on %s" % (box.name,))
    threads = []
    for team in box.teams:
        thread = threading.Thread(target=score_team, args=(box, team))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join(timeout=TIMEOUT + 1)


def score_team(box, team):
    ''' Executed as a thread: scores a single team '''
    auth = AuthenticateReporter(box, team)
    auth.check_validity()
    if auth.confirmed_access != None:
        award_money(box, team, auth)
    else:
        team.boxes.remove(box)
        dbsession.add(team)
        dbsession.flush()
        message = "Lost communication with bot on %s." % box.name
        Notifier.team_warning("Lost Access", message)


def award_money(box, team, auth):
    ''' Awards money if everything authenticated properly '''
    team = Team.by_id(team.id) # Refresh object
    if auth.confirmed_access == 'root':
        team.money += box.root_award
    else:
        team.money += box.user_award
    dbsession.add(team)
    dbsession.flush()


class AuthenticateReporter(object):
    ''' Authenticates a remote reporter '''

    def __init__(self, box, team):
        self.sha = sha256()
        self.box = box
        self.port = team.listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.confirmed_access = None
        self.pending_access = None

    def check_validity(self):
        ''' Checks the validity of a reporter on a box '''
        logging.info("Checking for reporter -> %s:%s" % (self.box.
                                                         ip_address, self.port))
        try:
            self.sock.connect((self.box.ip_address, self.port))
            self.pending_access = self.sock.recv(BUFFER_SIZE)
            if self.pending_access.lower() == 'root':
                self.sha.update(self.box.root_key)
                self.verify_response()
            elif self.pending_access.lower() == 'user':
                self.sha.update(self.box.user_key)
                self.verify_response()
            else:
                logging.info("Reporter provided an invalid access level.")
        except:
            logging.info("Failed to connect to reporter.")

    def verify_response(self):
        ''' Verifies zero-knowledge proof '''
        self.send_xid()
        response = self.sock.recv(BUFFER_SIZE)
        if response == self.sha.hexdigest():
            if self.pending_access == 'root':
                self.confirmed_access = u'root'
            else:
                self.confirmed_access = u'user'
        else:
            logging.warn("Reporter's response was invalid.")

    def send_xid(self):
        ''' Sends transaction id to client '''
        xid = b64encode(urandom(XID_SIZE))
        self.sock.sendall(xid)
        self.sha.update(xid)
