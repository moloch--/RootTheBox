 Root the Box
-------------------
* A multi-threaded real-time scoring engine for hacker CTF games
* Based on tornado/teaspoon
* Licensed under the Apache License, Version 2.0

Features
-------------------
* Real-time scoreboard graphs using web sockets
* Real-time status updates using web sockets
* Team based file/text sharing
* HTML5/CSS3 stuff
* A wall of sheep displaying cracked passwords
* Saxroll 403 page
* Other cool stuff

 Setup
-------------------
* Supported platforms: Ubuntu 11.10, but should work on any linux system.  Windows and OSX have not been tested.
* Install these packages: tornado (2.2), sqlalchemy (0.7.5), python-recaptcha, python-jsonpickle
* Detailed setup instructions are in the Github wiki, here is the tl;dr
* Run the __depends.sh__ script in /setup to automatically install required packages
* Set up the db connection string at __models/\_\_init\_\_.py__
* 'python . create' to ONLY create the tables 
* 'python -c "import setup.auth"' to create the admin account
* 'python . serve' - will serve the application
*  For more configuration checkout __handlers/\_\_init\_\_.py__

SLOC Information
---------------------

Totals grouped by language (dominant language first):

python:        3028 (99.54%)

sh:              14 (0.46%)

Total Physical Source Lines of Code (SLOC)                = 3,042

Total Estimated Cost to Develop                           = $ 86,888 (average salary = $56,286/year, overhead = 2.40).

Generated using David A. Wheeler's 'SLOCCount'

