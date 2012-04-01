#!/usr/bin/env python

'''
Created on Feb 24, 2012

@author: moloch
'''

import os
import time
import socket
import random
import urllib
import httplib

from hashlib import sha256

class RtbClient():

    def __init__(self, display_name):
        self.listenPort = None
        self.user = urllib.urlencode({'handle': display_name})
        self.rHost = '127.0.0.1'
        self.loadKeyFile()
    
    def start(self):
        if self.register():
            self.reporter()
        else:
            print 'failure'
    
    def loadKeyFile(self):
        self.keyValue = '1234'
    
    def reporter(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print 'binding to port', self.listenPort
        sock.bind(("", self.listenPort))
        sock.listen(1)
        while True:
            try:
                print 'rep listening...'
                connection, address = sock.accept()
                print 'connection from', address[0]
                if address[0] != self.rHost:
                    print 'impostor!'
                    connection.sendall("Impostor\r\n")
                    connection.close()
                else:
                    checksum = sha256()
                    connection.sendall('root')
                    xid = connection.recv(1024)
                    print 'Got xid:', xid
                    checksum.update(self.keyValue + xid)
                    result = checksum.hexdigest()
                    time.sleep(0.1)
                    connection.sendall(result)
                    print 'rep sent: ', result
            except socket.error:
                os._exit(1)
    
    def register(self):
        connection = httplib.HTTPConnection("127.0.0.1:8888")
        connection.request("GET", "/reporter/register?%s" % self.user)
        response = connection.getresponse()
        if response.status == 200:
            data = response.read()
            try:
                self.listenPort = int(data)
                return True
            except:
                print 'Error:', data
        return False
        
if __name__ == '__main__':
    client = RtbClient('moloch')
    client.start()
