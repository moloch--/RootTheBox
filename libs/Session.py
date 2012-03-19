'''
Created on Mar 13, 2012

@author: moloch
'''

from os import urandom
from base64 import b64encode
from threading import Lock
from libs.Singleton import *
from datetime import datetime, timedelta

@Singleton
class SessionManager():
	''' Mostly thread safe session manager '''
	
	def __init__(self):
		self.sessions = {}
		self.sessions_lock = Lock()

	def clean_up():
		''' Removes all expired sessions '''
		for sid in self.sessions.keys():
			if self.sessions[sid].is_expired():
				self.sessions_lock.acquire()
				del self.sessions[sid]
				self.sessions_lock.release()

	def start_session(self):
		''' Creates a new session and returns the session id and the new session object '''
		sid = b64encode(urandom(24))
		self.sessions_lock.acquire()
		self.sessions[sid] = Session()
		self.sessions_lock.release()
		return sid, self.sessions[sid]

	def remove_session(self, sid):
		''' Removes a given session '''
		if sid in self.sessions.keys():
			self.sessions_lock.acquire()
			del self.sessions[sid]
			self.sessions_lock.release()

	def get_session(self, sid, ip_address):
		''' Returns a session object if it exists or None '''
		if sid in self.sessions.keys():
			if self.sessions[sid].is_expired():
				self.remove_session(sid)
			elif self.sessions[sid].data['ip'] == ip_address:
				return self.sessions[sid]
		return None

class Session():
	def __init__(self):
		self.id = ''
		self.data = {}
		self.expiration = datetime.now() + timedelta(minutes = 20)
		
	def is_expired(self):
		''' Returns boolean based on if session has expired '''
		return (timedelta(0) < (datetime.now() - self.expiration))
