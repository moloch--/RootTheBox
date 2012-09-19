# -*- coding: utf-8 -*-
"""
Sessions module for the Tornado framework.
Milan Cermak <milan.cermak@gmail.com>
Hacked up by Moloch

This module implements sessions for Tornado.
Using Memcached.

USAGE:
======

Every session object can be handled as a dictionary:
    self.session[key] = value
    var = self.session[key]

The session data is saved automatically for you when the request
handler finishes.

Two utility functions, invalidate() and refresh() are available to
every session object. Read their documentation to learn more.

The application provider is responsible for removing stale, expired
sessions from the storage. However, he can use the delete_expired()
function provided with every storage class except Memcached, which
knows when a session expired and removes it automatically.


SETTINGS:
=========

The session module introduces new settings available to the
application:

session_age: how long should the session be valid (applies also to cookies);
             the value can be anything an integer, long, string or datetime.timedelta;
             integer, long and string are meant to represent seconds,
             default is 900 seconds (15 mins);
             check out _expires_at for additional info

session_regeneration_interval: period in seconds, after which the session_id should be
                               regenerated; when the session creation time + period
                               exceed current time, a new session is stored
                               server-side (the sesion data remains unchanged) and
                               the client cookie is refreshed; the old session
                               is no longer valid
                               session regeneration is used to strenghten security
                               and prevent session hijacking; default interval
                               is 4 minutes
                               the setting accepts integer, string or timedelta values,
                               read _next_regeneration_at() documentation for more info

session_cookie_name: the name of the cookie, which stores the session_id;
                     default is 'session_id'

session_cookie_path: path attribute for the session cookie;
                     default is '/'

session_cookie_domain: domain attribute for the session cookie;
                       default is None

session_security_model: not implemented yet;
                        the plan to future versions is to provide some basic
                        mechanisms to prevent session hijacking, based on
                        users IP address, User-Agent, GeoIP or whatever
                        other data; suggestions welcomed
"""

import base64
import collections
import datetime
import os
import cPickle as pickle
import re
import time
import types

SID_SIZE = 32  # Size in bytes


class BaseSession(collections.MutableMapping):
    """
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
    of the already available classes and documentation to aformentioned functions.
    """
    def __init__(self, session_id=None, data=None, security_model=[], expires=None,
                 duration=None, ip_address=None, user_agent="",
                 regeneration_interval=None, next_regeneration=None, **kwargs):
        # if session_id is True, we're loading a previously initialized session
        if session_id:
            self.session_id = session_id
            self.data = data
            self.duration = duration
            self.expires = expires
            self.dirty = False
        else:
            self.session_id = self._generate_session_id()
            self.data = {}
            self.duration = duration
            self.expires = self._expires_at()
            self.dirty = True

        self.ip_address = ip_address
        self.user_agent = user_agent
        self.security_model = security_model
        self.regeneration_interval = regeneration_interval
        self.next_regeneration = next_regeneration or self._next_regeneration_at(
        )
        self._delete_cookie = False

    def __repr__(self):
        return '<Session id: %s -> Data: %s>' % (self.session_id, self.data)

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
        return os.urandom(SID_SIZE).encode('hex')  # 256 bits of entropy

    def _is_expired(self):
        """Check if the session has expired."""
        if self.expires is None:  # never expire
            return False
        return datetime.datetime.utcnow() > self.expires

    def _expires_at(self):
        """Find out the expiration time. Returns datetime.datetime."""
        v = self.duration
        if v is None:  # never expire
            return None
        elif isinstance(v, datetime.timedelta):
            pass
        elif isinstance(v, (int, long)):
            self.duration = datetime.timedelta(seconds=v)
        elif isinstance(v, basestring):
            self.duration = datetime.timedelta(seconds=int(v))
        else:
            self.duration = datetime.timedelta(seconds=900)  # 15 mins

        return datetime.datetime.utcnow() + self.duration

    def _serialize_expires(self):
        """ Determines what value of expires is stored to DB during save()."""
        if self.expires is None:
            return None
        else:
            return int(time.mktime(self.expires.timetuple()))

    def _should_regenerate(self):
        """Determine if the session_id should be regenerated."""
        if self.regeneration_interval is None:  # never regenerate
            return False
        return datetime.datetime.utcnow() > self.next_regeneration

    def _next_regeneration_at(self):
        """Return a datetime object when the next session id regeneration
        should occur."""
        # convert whatever value to an timedelta (period in seconds)
        # store it in self.regeneration_interval to prevent
        # converting in later calls and return the datetime
        # of next planned regeneration
        v = self.regeneration_interval
        if v is None:  # never regenerate
            return None
        elif isinstance(v, datetime.timedelta):
            pass
        elif isinstance(v, (int, long)):
            self.regeneration_interval = datetime.timedelta(seconds=v)
        elif isinstance(v, basestring):
            self.regeneration_interval = datetime.timedelta(seconds=int(v))
        else:
            self.regeneration_interval = datetime.timedelta(
                seconds=240)  # 4 mins

        return datetime.datetime.utcnow() + self.regeneration_interval

    def invalidate(self):
        """Destorys the session, both server-side and client-side.
        As a best practice, it should be used when the user logs out of
        the application."""
        self.delete()  # remove server-side
        self._delete_cookie = True  # remove client-side

    def refresh(self, duration=None, new_session_id=False):  # the opposite of invalidate
        """Prolongs the session validity. You can specify for how long passing a
        value in the duration argument (the same rules as for session_age apply).
        Be aware that henceforward this particular session may have different
        expiry date, not respecting the global setting.

        If new_session_id is True, a new session identifier will be generated.
        This should be used e.g. on user authentication for security reasons."""
        if duration:
            self.duration = duration
            self.expires = self._expires_at()
        else:
            self.expires = self._expires_at()
        if new_session_id:
            self.delete()
            self.session_id = self._generate_session_id()
            self.next_regeneration = self._next_regeneration_at()
        self.dirty = True  # force save
        self.save()

    def save(self):
        """Save the session data and metadata to the backend storage
        if necessary (self.dirty == True). On successful save set
        dirty to False."""
        pass

    @staticmethod
    def load(session_id, location):
        """Load the stored session from storage backend or return
        None if the session was not found, in case of stale cookie."""
        pass

    def delete(self):
        """Remove all data representing the session from backend storage."""
        pass

    @staticmethod
    def delete_expired(file_path):
        """Deletes sessions with timestamps in the past form storage."""
        pass

    def serialize(self):
        dump = {'session_id': self.session_id,
                'data': self.data,
                'duration': self.duration,
                'expires': self.expires,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'security_model': self.security_model,
                'regeneration_interval': self.regeneration_interval,
                'next_regeneration': self.next_regeneration}
        return base64.encodestring(pickle.dumps(dump))

    @staticmethod
    def deserialize(datastring):
        return pickle.loads(base64.decodestring(datastring))

try:
    import pylibmc

    class MemcachedSession(BaseSession):
        """
        Class responsible for Memcached stored sessions. It uses the
        pylibmc library because it's fast. It communicates with the
        memcached server through the binary protocol and uses async
        I/O (no_block set to 1) to speed things up even more.

        Session ID is used as a key. The value consists of colon
        separated values of serializes session object, expiry timestamp,
        IP address and User-Agent.

        Values are stored with timeout set to the difference between
        saving time and expiry time in seconds. Therefore, no
        old sessions will be held in Memcached memory.
        """

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

        def _serialize_expires(self):
            """ Determines what value of expires is stored to DB during save()."""
            if self.expires is None:
                return '-1'
            else:
                return str(int(time.mktime(self.expires.timetuple())))

        def save(self):
            """
            Write the session to Memcached. Session ID is used as
            key, value is constructed as colon separated values of
            serialized session, session expiry timestamp, ip address
            and User-Agent.
            The value is not stored indefinitely. It's expiration time
            in seconds is calculated as the difference between the saving
            time and session expiry.
            """
            if not self.dirty:
                return
            value = ':'.join((self.serialize(),
                              self._serialize_expires(),
                              self.ip_address,
                              self.user_agent))
            # count how long should it last and then add or rewrite
            if self.expires is None:
                # set expiry 30 days, max for memcache
                # http://code.google.com/p/memcached/wiki/FAQ#What_are_the_limi
                # ts_on_setting_expire_time?_%28why_is_there_a_30_d
                self.connection.set(
                    self.session_id, value, time=timedelta.max.seconds * 30)
            else:
                live_sec = self.expires - datetime.datetime.utcnow()
                self.connection.set(
                    self.session_id, value, time=live_sec.seconds)
            self.dirty = False

        @staticmethod
        def load(session_id, connection):
            """Load the session from storage."""
            try:
                value = connection.get(session_id)
                if value:
                    data = value.split(':', 1)[0]
                    kwargs = MemcachedSession.deserialize(data)
                    return MemcachedSession(connection, **kwargs)
            except:
                return None
            return None

        def delete(self):
            """Delete the session from storage."""
            self.connection.delete(self.session_id)

except ImportError:
    pass
