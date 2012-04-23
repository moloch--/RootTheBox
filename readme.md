#> Root the Box

A Game of Hackers
-------------------
Root the Box is a multi-threaded real-time scoring engine for a computer wargame where hackers can practice and learn. 
The application can be easily modified for any hacker CTF game.

Features
-------------------
* Based on Tornado
* Distributed under the Apache License, Version 2.0
* Real-time scoreboard graphs using web sockets
* Real-time status updates using web sockets
* Team based file/text sharing
* A wall of sheep displaying cracked passwords
* Lots of HTML5 & CSS3
* Saxroll 403 page
* Other cool stuff

Setup
-------------------
Detailed setup instructions https://github.com/moloch--/RootTheBox/wiki/Installation

Setup TL;DR
-------------------
* Python 2.5.x - 2.7.x
* Supported platforms: Ubuntu 11.10, but should work on any linux system.  Windows and OSX have not been tested.
* Install these packages: tornado (2.2), sqlalchemy (0.7.5), python-recaptcha, python-jsonpickle
* Run the __depends.sh__ script in /setup to automatically install required packages
* Set up the db connection string ing __models/\_\_init\_\_.py__
* 'python . create' to create the database tables 
* 'python -c "import setup.auth"' to create the admin account
* 'python . serve' - will start the application
*  For more configuration checkout __handlers/\_\_init\_\_.py__

SLOC Information
---------------------
SLOC	Directory	SLOC-by-Language (Sorted)
1480    handlers        python=1480
869     libs            python=869
656     models          python=656
267     tests           python=267
188     flag            python=188
47      setup           python=33,sh=14
28      top_dir         python=28
26      modules         python=26

Totals grouped by language (dominant language first):

python:        3547 (99.61%)

sh:              14 (0.39%)

Total Physical Source Lines of Code (SLOC)                = 3,561

Total Estimated Cost to Develop                           = $ 102,516

Generated using David A. Wheeler's 'SLOCCount'

