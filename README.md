# >\_ Root the Box

[![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?raw=true&sanitize=true)](https://github.com/moloch--/RootTheBox/blob/master/LICENSE)
[![Code style:
black](https://img.shields.io/badge/code%20style-black-000000.svg?raw=true&sanitize=true)](https://github.com/ambv/black)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/apsdehal/awesome-ctf)

Root the Box is a real-time capture the flag (CTF) scoring engine for computer wargames where hackers can practice and learn. The application can be easily configured and modified for any CTF style game. The platform allows you to engage novice and experienced players alike by combining a fun game-like environment with realistic challenges that convey knowledge applicable to the real-world, such as penetration testing, incident response, digital forensics and threat hunting.

![example](static/images/example.png?raw=true)

Like traditional CTF games, each team or player can target challenges of varying difficulty and sophistication, attempting to collect flags. But Root the Box brings additional options to the game.  It has built-in support for "botnets", allowing players to upload a small bot program to target machines that grant periodic rewards for each bot in the botnet.  You have the option to use a banking system, where (in-game) money can be used instead of points to unlock new levels, buy hints to flags, download a target's source code, or even "SWAT" other players.  Password hashes for player bank accounts can also be publicly displayed, allowing competitors to crack them and steal each other's money.

## Screenshots & Demo
Additional platform [screenshots](https://github.com/moloch--/RootTheBox/wiki/Screenshots) and game examples.

[RootTheBox Demo](https://rootthebox.herokuapp.com/) – _Note it may take a few seconds to wake up. Also, please don't change passwords on the example accounts, but feel free to register a new user._
-   Admin Username `admin` Password `rootthebox`
-   Player Username `player` Password `rootthebox`

## Features

-   Team Play or Individual Play
-   Real-time animated scoreboard, graphs, and status updates using websockets
-   Flag Types: Static, Regex, Datetime, Multiple Choice, File - w/options for case sensitivity
-   Options for Penalties, Hints, Attempts, Level Bonuses, Dynamic Scoring, Categories and more
-   Built-in team based file/text sharing and Admin game material distirbution
-   Chat support with [Rocket Chat](https://rocket.chat/) integration
-   [CTF Time](https://ctftime.org/) compatible JSON scoreboard feed
-   Supports [OWASP Juice Shop CTF](https://github.com/bkimminich/juice-shop-ctf) export
-   Freeze scoreboard at a specific time allowing for end game countdown
-   Optional Story Mode - Supports intro dialog, capture Flag or Section dialog w/graphics
-   Optional [in-game Botnets](https://github.com/moloch--/RootTheBox/wiki/Features) or wall of sheep displaying cracked passwords
-   Unlocks and upgrades as users capture flags
-   Export and share Boxes/Flags
-   Multiple Language Support
-   Site Themes and other cool stuff

## Setup

See the [Root the Box Wiki](https://github.com/moloch--/RootTheBox/wiki)

## Platform Requirements

-   [Python 2.7.x or <= 3.8.x](https://www.python.org/), [PyPy](http://pypy.org/) or [Docker](https://github.com/moloch--/RootTheBox/wiki/Docker-Deployment).  (*Note: Python 3.9 breaks thigns as it removes Py2/3 compatibility.*)
-   Install scripts are for [Ubuntu](http://www.ubuntu.com/) >= 18.04 (or [Debian](https://www.debian.org/)) but the application should work on any recent Linux, BSD, or OSX system.

## Questions? Problems? Feature Requests?

[Create an issue](https://github.com/moloch--/RootTheBox/issues) on GitHub if you have any questions, problems or feature requests. We're happy to help you out with setup/configuration/edits and we're always brainstorming new ideas and looking for cool stuff to add!

## Contributing

We welcome code contributions, please [see our contributing guidelines](https://github.com/moloch--/RootTheBox/blob/master/CONTRIBUTING.md) on the wiki for more information.
