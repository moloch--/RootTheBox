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

More details: [Root the Box](http://root-the-box.com/)

Features
-------------------
* [Distributed under the Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
* [Team based botnets](https://github.com/moloch--/RootTheBox/wiki/Features)
* Real-time scoreboard graphs using websockets
* Real-time status updates using websockets
* Built-in team based file/text sharing
* A wall of sheep displaying cracked passwords
* Unlocks and upgrades as users caputre flags
* Supports MySQL, SQLite, or Postgresql
* Export and share Boxes/Flags (or backup)
* Lots of HTML5 & CSS3
* Other cool stuff

Setup
-------------------
See [detailed setup instructions](https://github.com/moloch--/RootTheBox/wiki/Installation)

Setup TL;DR
-------------------
* Python 2.7.x / Tornado 3.1
* Supported platforms: Install scripts are for Ubuntu/Debian, but the application should work on any Linux, BSD, or OSX system.  Windows has not been tested.
* Run the __depends.sh__ script in __/setup__ to automatically install required packages (Ubuntu/Debian only)
* Set up the database connection settings in __rootthebox.cfg__ you will need to create the db/user manually
* Edit settings in __rootthebox.cfg__ to your liking, you can also manage many of these settings from the admin web ui
* __./rootthebox.py --create-tables__ to create, and initialize the database (only need to do this once)
* __./rootthebox.py --start__ To start the application
* You can import XML files (automatically setup Boxes/Flags) from the command line using __./rootthebox.py --xml game.xml__ 

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
CSS                             24            589             88          13702
Python                          67           2028            714           9490
HTML                            60            127             51           4772
Javascript                      33            175            100           2022
Bourne Shell                     2              8             26             20
-------------------------------------------------------------------------------
SUM:                           186           2927            979          30006
-------------------------------------------------------------------------------
```
