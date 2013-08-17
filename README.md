#> Root the Box

A Game of Hackers
-------------------
Root the Box is a real-time scoring engine for a computer wargames where hackers can practice and learn. 
The application can be easily modified for any hacker CTF game. Root the Box attempts to engage novice and experienced 
hackers alike by combining a fun game-like environment, with realistic challenges that convey knowledge applicable 
to real-world penetration testing. Just as in traditional CTF games, each team attacks targets of varying difficulty 
and sophistication, attempting to collect flags. However in Root the Box, teams can also create "Botnets" by uploading
a small bot program to target machines. Teams are periodically rewarded with (in-game) money for each bot in their botnet; 
the larger the botnet the larger the reward.

Money can be used to unlock new levels, buy hints to flags, download a target's source code, or even "SWAT" other players by bribing the (in-game) police.

Player's "bank account passwords" are also publically displayed by the scoring engine, allowing players to crack each other's passwords and steal each other's money.

More details: [Root the Box](http://rootthebox.com/)

Features
-------------------
* Distributed under the Apache License, Version 2.0
* Team based [botnets](https://github.com/moloch--/RootTheBox/wiki/Features)
* Real-time scoreboard graphs using web sockets
* Real-time status updates using web sockets
* Built-in team based file/text sharing
* A wall of sheep displaying cracked passwords
* Unlocks and upgrades as users caputre flags
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
* Run the __depends.sh__ script in __/setup__ to automatically install required packages (Ubuntu/Debian only)
* Set up the db connection settings in __rootthebox.cfg__ (you will need to create the database/dbuser manually)
* Edit settings in __rootthebox.cfg__ make sure to disable debug mode, etc for production
* __./rootthebox.py --create-tables__ to create, and init the database (only need to do this once)
* __./rootthebox.py --start__ To start the application
* You can also script the game setup, see/edit __setup/game.py__; to execute setup scripts run __./rootthebox.py --game__
* To access the recovery console run __./rootthebox.py --recovery__

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
CSS                             20            605             93          14646
Python                          64           1746            712           8440
HTML                            57            120             50           4694
Javascript                      21            169            309           1883
Bourne Shell                     2              8             26             19
-------------------------------------------------------------------------------
SUM:                           164           2648           1190          29682
-------------------------------------------------------------------------------
```
