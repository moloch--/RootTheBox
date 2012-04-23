#!/usr/bin/env python
'''
Created on Apr 23, 2012

@author: moloch

 Copyright [2012] [Redacted Labs]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
---------

Small program used by teams to monitor their flags
For the sake of portability everything is in one file

'''

###################
# > Imports
###################
import os
import sys
import socket

try:
	import curses
except ImportError:
	print("Error: Failed to import curses, platform not supported")
	os._exit(2)

###################
# > Simple Box
###################
class Box(object):

	def __init__(self, name, ip_address, port):
		self.name = name
		self.ip_address = ip_address
		self.port = port
		self.is_captured = False

###################
# > Flag Manager
###################
class FlagManager(object):

	def __init__(self):
     	self.boxes = []
     	self.display_name = None

    def start(self):
    	self.screen = curses.initscr()
		self.screen.clear()
     	self.screen.border(0)

    def load_file(self, path):
        ''' Reads a file at path returns the file contents or None '''
        path = os.path.abspath(path)
        if os.path.exists(path) and os.path.isfile(path):
            box_file = open(path, 'r')
            for line in box_file.readlines():
            	if len(line) == 0 or line[0] == "#":
            		continue
            	plain_text = line.strip()
            	name, ip_address, port = line.split(";")
            	self.boxes.append(Box(name, ip_address, port))
            box_file.close
        else:
        	sys.stdout.write("[!] Error: File does not exist (%s)\n" % (os.path.abspath(path),))
        	sys.stdout.flush()
        	os._exit(1)

    def load_url(self):
    	''' Load boxes from scoring engine '''
    	pass

	def __redraw__(self):
		starting_line = 2

	def __clear__(self):
		''' Clears the screen '''
		self.screen.clear()

	def stop(self):
		''' Gracefully exits the program '''
		curses.endwin()

###################
# > Main Entry
###################
def help():
	''' Displays a helpful message '''
	sys.stdout.write("Root the Box - Flag Manager\n")
	sys.stdout.write("Usage:\n")
	sys.stdout.write("\tFileManager.py <options>\n")
	sys.stdout.write("Options:\n")
	sys.stdout.write("\t-f, --file <path>...........................Load boxes from file\n")
	sys.stdout.write("\t-h, --hacker <hacker>.......................Define hacker name\n")
	sys.stdout.write("\t-u, --url <url>.............................Scoring engine URL\n")
	sys.stdout.flush()

def parse_argv(flag_manager):
	''' Parses command line arguments '''
	for arg in sys.argv:
		if arg == "-f" or arg == "--file":
			flag_manager.load_file(get_value(arg))
		elif arg == "-h" or arg == "--hacker":
			flag_manager.display_name = get_value(arg)
		elif arg == "-u" or "--url":
			flag_manager.load_url(get_value(arg))
		else:
			sys.stdout.write("[!] Error: Unknown parameter (%s)\n" % (arg,))
			sys.stdout.flush()
			os._exit(3)

def get_value(token):
	''' Gets a value based on a command line parameter '''
	try:
		index = sys.argv.index(token)
		if index + 1 < len(sys.argv):
			return sys.argv[index + 1]
		else:
			raise ValueError
	except ValueError:
		sys.stdout.write("[!] Error: No value for parameter (%s)\n" % (token,))
		sys.stdout.flush()
		os._exit(1)

if __name__ == "__main__":
	if "-h" in sys.argv or "--help" in sys.argv:
		help()
	else:
		flag_manager = FlagManager()
		if 1 <= len(sys.argv):
			parse_argv(flag_manager)
		flag_manager.start()
