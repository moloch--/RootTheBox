"""
Created on Feb 24, 2012

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

Requires Py2Exe, builds a .exe file for easy of use on windows
Current configuration requires administrator access if UAC is enabled

"""

from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
	options = {'py2exe': {'bundle_files': 1,'compressed': 1, 'optimize': 2}}, 
	windows = [{'script': 'Flag.py', 'uac_info': 'requireAdministrator', 'icon_resources': [(1, 'rtb.ico')] }],
	zipfile = None,
)
