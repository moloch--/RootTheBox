# >\_ Root the Box

[![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?raw=true&sanitize=true)](https://github.com/moloch--/RootTheBox/blob/master/LICENSE)
[![Code style:
black](https://img.shields.io/badge/code%20style-black-000000.svg?raw=true&sanitize=true)](https://github.com/ambv/black)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/apsdehal/awesome-ctf)

Root the Box is a real-time capture the flag (CTF) scoring engine for computer wargames where hackers can practice and learn. The application can be easily configured and modified for any CTF style game. The platform allows you to engage novice and experienced players alike by combining a fun game-like environment with realistic challenges that convey knowledge applicable to the real-world, such as penetration testing, incident response, digital forensics and threat hunting.

![example](static/images/example.png?raw=true)

## Screenshots & Demo
Additional platform [screenshots](https://github.com/moloch--/RootTheBox/wiki/Screenshots) and game examples.

[RootTheBox Demo](https://roottheboxdemo-ih63mtsgxa-uc.a.run.app/) – _Note it may take a few seconds to wake up. Also, please don't change passwords on the example accounts, but feel free to register a new user._
-   Admin Username `admin` Password `rootthebox`
-   Player Username `player` Password `rootthebox`

If you’re using RootTheBox, please ★Star this repository to show your interest!

## Features

-   Team Play or Individual Play
-   Real-time animated scoreboard, graphs, and status updates using websockets
-   Flag Types: Static, Regex, Datetime, Multiple Choice, File - w/options for case sensitivity
-   Options for Penalties, Hints, Attempts, Level Bonuses, Dynamic Scoring, Categories and more
-   Built-in team based file/text sharing and Admin game material distribution
-   Integrated [CyberChef](https://gchq.github.io/CyberChef/) in tools menu
-   Chat support, with optional [Rocket Chat](https://rocket.chat/) integration
-   [CTF Time](https://ctftime.org/) compatible JSON scoreboard feed
-   Supports [OWASP Juice Shop CTF](https://github.com/bkimminich/juice-shop-ctf) export
-   Freeze scoreboard at a specific time allowing for end game countdown
-   Optional Story Mode - Supports intro dialog, capture Flag or Section dialog w/graphics
-   Optional [Advanced Features](https://github.com/moloch--/RootTheBox/wiki/Features), such as in-game botnets, "SWAT" players, banking (in-game) money, and wall of sheep displaying cracked passwords
-   Allows for unlocks and upgrades as users capture flags
-   Export and share Boxes/Flags
-   Multiple Language Support
-   Deploy in the [Cloud](https://github.com/moloch--/RootTheBox/wiki/Cloud-Deployment), with [Docker](https://github.com/moloch--/RootTheBox/wiki/Docker-Deployment), or [Direct](https://github.com/moloch--/RootTheBox/wiki/Installation).
-   Site Themes and other cool stuff

## Setup

See the [Root the Box Wiki](https://github.com/moloch--/RootTheBox/wiki)

## Platform Requirements

-   [Python 3](https://www.python.org/), [PyPy](http://pypy.org/) or [Docker](https://github.com/moloch--/RootTheBox/wiki/Docker-Deployment).
-   Install scripts are for [Ubuntu](http://www.ubuntu.com/) >= 18.04 (or [Debian](https://www.debian.org/)) but the application should work on any recent Linux, BSD, MacOS, or Windows system.

## Questions? Problems? Feature Requests?

[Create an issue](https://github.com/moloch--/RootTheBox/issues) on GitHub if you have any questions, problems or feature requests. We're happy to help you out with setup/configuration/edits and we're always brainstorming new ideas and looking for cool stuff to add!

## Contributing

We welcome code contributions, please [see our contributing guidelines](https://github.com/moloch--/RootTheBox/blob/master/CONTRIBUTING.md) on the wiki for more information.
