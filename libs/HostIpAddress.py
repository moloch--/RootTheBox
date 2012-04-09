'''
Created on Mar 21, 2012

@author: moloch
'''
import socket
import logging

class HostIpAddress():

	def __init__(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect(("google.com", 80))
		self.ip_address = sock.getsockname()[0]
		logging.info("Resolved server ip address to %s" % (self.ip_address,))
		sock.close()

	def get_ip_address(self):
		return self.ip_address
