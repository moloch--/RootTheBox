#> Root the Box

A Game of Hackers
-------------------
Root the Box is a real-time scoring engine for a computer wargames where hackers can practice and learn. 
The application can be easily modified for any hacker CTF game.  Check out the [Root the Box website](http://rootthebox.com/)

Features
-------------------
* Distributed under the Apache License, Version 2.0
* Team based [botnets](https://github.com/moloch--/RootTheBox/wiki/Features)
* Real-time scoreboard graphs using web sockets
* Real-time status updates using web sockets
* Team based file/text sharing
* A wall of sheep displaying cracked passwords
* Unlocks and upgrades as users caputre flags (configurable)
* Lots of HTML5 & CSS3
* Saxroll 403 page
* Other cool stuff

Setup
-------------------
See [detailed setup instructions](https://github.com/moloch--/RootTheBox/wiki/Installation)

Setup TL;DR
-------------------
* Python 2.5.x - 2.7.x
* Supported platforms: Install script is for Ubuntu/Debian, but the application should work on any Linux or BSD system.  Windows and OSX have not been tested.
* Run the __depends.sh__ script in /setup to automatically install required packages (Ubuntu/Debian only)
* Set up the db connection settings in __rootthebox.cfg__ (you will need to create the database/dbuser manually)
* Edit settings in __rootthebox.cfg__ make sure to disable debug mode, etc for production
* Root the Box is a package so you can run the directory like so __python /RootTheBox --help__, or run \_\_main\_\_.py as a normal script
* 'python /RootTheBox --create-tables' to create, and init the database (only need to do this once)
* 'python /RootTheBox --start' To start the application
* You can also script the game setup, see __setup/game.py__ to execute setup scripts run 'python /RootTheBox --game'
* To access the recovery console run 'python /RootTheBox --recovery'

To Do
---------------------
* More documentation
* An actual stable release :D

Questions? Problems?
-------------------------------
Open a ticket on GitHub and I'd be happy to help you out with setup/configuration/edits.

Feature Requests
----------------------
Open a ticket on GitHub, and I'll see what I can do for you.  I'm always brainstorming new ideas, and looking for cool stuff to add!


Other
----------------

```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
CSS                             19            604             82          14631
Python                          64           1561            503           7380
HTML                            52            100             60           4144
Javascript                      24            199            460           2385
Bourne Shell                     2              8             26             19
-------------------------------------------------------------------------------
SUM:                           161           2472           1131          28559
-------------------------------------------------------------------------------
```
