#> Root the Box

A Game of Hackers
-------------------
Root the Box is a real-time scoring engine for a computer wargames where hackers can practice and learn. 
The application can be easily modified for any hacker CTF game.  More details at http://rootthebox.com/

Features
-------------------
* Based on the TornadoWeb framework
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
* Supported platforms: Install script is for Ubuntu/Debian, but the application should work on any Linux or BSD system.  Windows and OSX have not been tested.
* Run the __depends.sh__ script in /setup to automatically install required packages (Ubuntu/Debian only)
* Set up the db connection settings in __rootthebox.cfg__ (you will need to create the database/dbuser manually)
* 'python /RootTheBox --create-tables' to create, and init the database
* 'python /RootTheBox --start' To start the application
* 'python /RootTheBox --help' for more options, or see __rootthebox.cfg__

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
