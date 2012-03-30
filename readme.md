 Root the Box
-------------------
* A multi-threaded real-time scoring engine for hacker CTF games
* Based on tornado/teaspoon
* http://rootthebox.com/
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
* install these packages: tornado (2.2), sqlalchemy (0.7.5), nose (1.0.0), python-recaptcha, python-jsonpickle, pycco and virtualenv is recommended
* set up the db connection string at __models/\_\_init\_\_.py__
* 'python . create' to ONLY create the tables 
* 'python -c "import setup.auth" to create the admin account
* 'python . test' - will test the application.
* 'python . serve' - will serve the application
*  For more configuration checkout __handlers/\_\_init\_\_.py__


