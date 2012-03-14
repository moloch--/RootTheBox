'''
Root the Box - Authenticate Reporter
Created on Feb 28, 2012

@author: moloch
'''

import time
import socket
import logging

from os import urandom
from hashlib import sha256
from base64 import b64encode
from tornado import iostream #@UnresolvedImport

TIMEOUT = 1
BUFFER_SIZE = 1024

class AuthenticateReporter():

    def __init__(self, box, port):
        self.sha = sha256()
        self.box = box
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        self.tcpStream = iostream.IOStream(sock, max_buffer_size=BUFFER_SIZE)
        self.tcpStream.set_close_callback(self.setDone)
        logging.info("Checking for reporter at %s:%s" % (self.box.ip_address, self.port))
        self.tcpStream.connect((self.box.ip_address, self.port))
        self.confirmedAccess = None
        self.pendingAccess = None
        self.done = False
    
    def setDone(self):
        ''' Set flag when authentication protocol has completed '''
        self.done = True
    
    def checkValidity(self):
        ''' Checks the validity of a reporter on a box '''
        try:
            self.tcpStream.read_bytes(len('root'), self.checkAccessLevel)
            time.sleep(TIMEOUT)
            if not self.done:
                logging.info("A reporter stopped responding on %s" % self.box.ip_address)
                self.kill()
        except socket.error, error:
            logging.info("Failed to connect to host %s: %s" % (self.box.ip_address, error))
            self.setDone()

    def checkAccessLevel(self, pendingAccess):
        ''' Check if the reporter provided a valid access level '''
        self.pendingAccess = pendingAccess
        if self.pendingAccess == 'root':
            self.sha.update(self.box.rootKey)
            self.sendXid()
        elif self.pendingAccess == 'user':
            self.sha.update(self.box.userKey)
            self.sendXid()
        else:
            logging.info("A reporter submitted an invalid access level")
            self.tcpStream.write("Error - Invalid access level %s" % self.pendingAccess)
            self.tcpStream.close()

    def sendXid(self):
        ''' Send the reporter the transaction id '''
        xid = self.getXid()
        self.tcpStream.write(xid)
        self.sha.update(xid)
        while self.tcpStream.writing():
            time.sleep(0.01)
        self.tcpStream.read_bytes(len(self.sha.hexdigest()), self.checkResponse)
            
    def checkResponse(self, response):
        ''' Checks if the reporter provided a valid response '''
        if self.sha.hexdigest() == response:
            self.tcpStream.write("Success")
            self.confirmedAccess = (self.pendingAccess == 'root')
            self.tcpStream.close()
        else:
            logging.info("A reporter submitted an invalid sha")
            self.tcpStream.write("Error - Checksum mismatch")
            self.tcpStream.close()

    def getXid(self):
        ''' Returns a randomly generated transaction id of XID_SIZE '''
        return b64encode(urandom(24))

    def kill(self):
        ''' Kills the connection to the reporter regardless of state '''
        self.tcpStream.close()
