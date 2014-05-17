# -*- coding: utf-8 -*-
'''
@author: Milan Cermak <milan.cermak@gmail.com>
@author: Moloch

This module implements sessions for Tornado using Memcached.
'''


import re
import os
import time
import json
import base64
import pylibmc
import logging
import collections

from os import _exit
from datetime import datetime, timedelta

ID_SIZE = 16  # Size in bytes
DURATION = 30  # Minutes

class BaseSession(collections.MutableMapping):
    '''
    The base class for the session object. Work with the session object
    is really simple, just treat is as any other dictionary:

    class Handler(tornado.web.RequestHandler):
        def get(self):
            var = self.session['key']
            self.session['another_key'] = 'value'

    Session is automatically saved on handler finish. Session expiration
    is updated with every request. If configured, session ID is
    regenerated periodically.

    The session_id attribute stores a unique, random, 64 characters long
    string serving as an indentifier.

    To create a new storage system for the sessions, subclass BaseSession
    and define save(), load() and delete(). For inspiration, check out any
    of the already available classes and documentation to aformentioned
    functions.
    '''
    def __init__(self, session_id=None, data=None, expires=None, ip_address=None,  **kwargs):
        # if session_id is True, we're loading a previously initialized session
        if session_id:
            self.session_id = session_id
            self.data = data if data else {}
            self.expires = expires
            self.dirty = False
        else:
            self.session_id = self._generate_session_id()
            self.data = {}
            self.expires = self._expires_at()
            self.dirty = True
        self.ip_address = ip_address

    def __repr__(self):
        return '<Session id: %s, Expires: %s>' % (self.session_id, self.expires)

    def __str__(self):
        return self.session_id

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.dirty = True

    def __delitem__(self, key):
        del self.data[key]
        self.dirty = True

    def keys(self):
        return self.data.keys()

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data.keys())

    def _generate_session_id(cls):
        return os.urandom(ID_SIZE).encode('hex')

    def is_expired(self):
        '''Check if the session has expired.'''
        return datetime.utcnow() > self.expires

    def _expires_at(self):
        return datetime.utcnow() + timedelta(minutes=DURATION)

    def refresh(self):
        self.expires = self._expires_at()
        self.dirty = True

    def extend_by(self, minutes):
        self.expires += timedelta(minutes=minutes)
        self.dirty = True

    def save(self):
        '''Save the session data and metadata to the backend storage
        if necessary (self.dirty == True). On successful save set
        dirty to False.'''
        pass

    @staticmethod
    def load(session_id, location):
        '''Load the stored session from storage backend or return
        None if the session was not found, in case of stale cookie.'''
        pass

    def delete(self):
        '''Remove all data representing the session from backend storage.'''
        pass

    def serialize(self):
        ''' We use JSON instead of Pickles '''
        dump = {
            'session_id': self.session_id,
            'data': self.data,
            'expires': str(self.expires),
            'ip_address': self.ip_address,
        }
        return json.dumps(dump).encode('base64').strip()

    @staticmethod
    def deserialize(datastring):
        dump = json.loads(datastring.decode('base64'))
        dump['expires'] = datetime.strptime(dump['expires'], "%Y-%m-%d %H:%M:%S.%f")
        return dump


class MemcachedSession(BaseSession):
    '''
    Class responsible for Memcached stored sessions. It uses the
    pylibmc library because it's fast. It communicates with the
    memcached server through the binary protocol and uses async
    I/O (no_block set to 1) to speed things up even more.

    Session ID is used as a key. The value consists of colon
    separated values of serializes session object, expiry timestamp,
    IP address

    Values are stored with timeout set to the difference between
    saving time and expiry time in seconds. Therefore, no
    old sessions will be held in Memcached memory.
    '''

    def __init__(self, connection, **kwargs):
        super(MemcachedSession, self).__init__(**kwargs)
        self.connection = connection
        if not 'session_id' in kwargs:
            self.save()

    @staticmethod
    def _parse_connection_details(details):
        if len(details) > 12:
            return re.sub('\s+', '', details[12:]).split(',')
        else:
            return ['127.0.0.1']

    def save(self):
        '''
        Write the session to Memcached. Session ID is used as
        key, value is constructed as colon separated values of
        serialized session, session expiry timestamp, ip address
        The value is not stored indefinitely. It's expiration time
        in seconds is calculated as the difference between the saving
        time and session expiry.
        '''
        if self.dirty:
            #logging.debug("[Memcached] Saving session with ID '%s'" % self.session_id)
            ttl = self.expires - datetime.utcnow()
            #logging.debug("[Memcached] Serialized -> %s" % self.serialize().decode('base64'))
            self.connection.set(str(self.session_id), self.serialize(), time=ttl.seconds)
            self.dirty = False

    @staticmethod
    def load(connection, session_id, ip_address):
        '''Load the session from storage.'''
        #logging.debug("[Memcached] Loading session with ID '%s'" % session_id)
        session = None
        try:
            value = connection.get(session_id)
            #logging.debug('[Memcached] Got back %s' % value.decode('base64'))
            if value:
                kwargs = MemcachedSession.deserialize(value)
                session = MemcachedSession(connection, **kwargs)
        except:
            logging.exception("[Memcached] Error while grabbing session data")
        return session

    def delete(self):
        '''Delete the session from storage.'''
        self.connection.delete(self.session_id)
