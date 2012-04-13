#
#  Build Script by Moloch
#  Requires Py2Exe for Python 2.7
#
from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
	options = {'py2exe': {'bundle_files': 1,'compressed': 1, 'optimize': 2}}, 
	windows = [{'script': 'RtbClient.py', 'uac_info': 'requireAdministrator', 'icon_resources': [(1, 'rtb.ico')] }],
	zipfile = None,
)
