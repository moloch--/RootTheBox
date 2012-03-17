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
from hashlib import sha256
from base64 import b64encode
from tornado import iostream #@UnresolvedImport
from models import Box

TIMEOUT = 1
BUFFER_SIZE = 1024

def scoring():
    results = {}
    boxes = list(Box.get_all())
    for box in boxes:
        threads = []
        for team in box.teams:
            auth = AuthenticateReporter(box, team)
            thread = threading.Thread(target = check_reporter, args = (box, team))
            threads.append(thread)
            thread.start()
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        # Remove failed connections


def check_reporter(self, box, team):
    ''' Authenticates remote service, returns True/False/None '''
    auth_handler = AuthenticationHandler(box, team)
    auth_handler.check_validity()
    if auth_handler.confirmed_access == None:
        return None
    else:
        return bool(auth_handler.confirmed_access)


class AuthenticateReporter():

    def __init__(self, box, team):
        self.sha = sha256()
        self.box = box
        self.team = team
        self.port = team.listen_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        self.tcp_stream = iostream.IOStream(sock, max_buffer_size=BUFFER_SIZE)
        self.tcp_stream.set_close_callback(self.setDone)
        logging.info("Checking for reporter at %s:%s" % (self.box.ip_address, self.port))
        self.tcp_stream.connect((self.box.ip_address, self.port))
        self.confirmed_access = None
        self.pending_access = None
        self.done = False
    
    def set_done(self):
        ''' Set flag when authentication protocol has completed '''
        self.done = True
    
    def check_validity(self):
        ''' Checks the validity of a reporter on a box '''
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
        self.tcp_stream.read_bytes(len(self.sha.hexdigest()), self.checkResponse)
            
    def check_response(self, response):
        ''' Checks if the reporter provided a valid response '''
        if self.sha.hexdigest() == response:
            self.tcp_stream.write("Success")
            self.confirmed_access = (self.pending_access == 'root')
            self.tcp_stream.close()
        else:
            logging.info("A reporter submitted an invalid sha")
            self.tcp_stream.write("Error - Checksum mismatch")
            self.tcp_stream.close()

    def get_xid(self):
        ''' Returns a randomly generated transaction id of XID_SIZE '''
        return b64encode(urandom(24))

    def kill(self):
        ''' Kills the connection to the reporter regardless of state '''
        self.tcp_stream.close()
