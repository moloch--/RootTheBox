'''
Created on Mar 21, 2012

@author: moloch
'''
import socket

class HostIpAddress():

	def __init__(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect(("gmail.com", 80))
		self.ip_address = sock.getsockname()[0]
		sock.close()

	def get_ip_address(self):
		return self.ip_address
