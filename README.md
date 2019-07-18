# >\_ Root the Box

[![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?raw=true&sanitize=true)](https://github.com/gchq/CyberChef/blob/master/LICENSE)

Root the Box is a real-time capture the flag (CTF) scoring engine for computer wargames where hackers can practice and learn. The application can be easily configured and modified for any CTF style game. The platform allows you to engage novice and experienced players alike by combining a fun game-like environment with realistic challenges that convey knowledge applicable to the real-world, such as penetration testing, incident response, digital forensics and threat hunting.

Like traditional CTF games, each team or player can target challenges of varying difficulty and sophistication, attempting to collect flags. But Root the Box brings additional options to the game.  It has built-in support for "botnets", allowing players to upload a small bot program to target machines that grant periodic rewards for each bot in the botnet.  You have the option to use a banking system, where (in-game) money can be used instead of points to unlock new levels, buy hints to flags, download a target's source code, or even "SWAT" other players.  Password hashes for player bank accounts can also be publicly displayed, allowing competitors to crack them and steal each other's money.

![example](static/images/example.png?raw=true)

## Screenshots
Additional platform [screenshots](https://github.com/moloch--/RootTheBox/wiki/Screenshots) and game examples

## Features

-   Team Play or Individual Play
-   Real-time animated scoreboard, graphs, and status updates using websockets
-   Flag Types: Static, Regex, Datetime, Multiple Choice, File - w/options for case senstivity
-   Options for Penalties, Hints, Attempts, Level Bonuses, Dynamic Scoring, Categories and more
-   Built-in team based file/text sharing and Admin game material distirbution
-   Chat support with [Rocket Chat](https://rocket.chat/) integration
-   Freeze Scores at a specific time allowing for end game countdown
-   Optional Story Mode - Supports intro dialog, capture Flag or Section dialog w/graphics
-   Optional [in-game Botnets](https://github.com/moloch--/RootTheBox/wiki/Features) or wall of sheep displaying cracked passwords
-   Unlocks and upgrades as users capture flags
-   Export and share Boxes/Flags
-   Site Themes and other cool stuff

## Setup

See the [Root the Box Wiki](https://github.com/moloch--/RootTheBox/wiki)

## Platform Requirements

-   [Python 2.7.x or 3.6.x](https://www.python.org/), [Pypy 2.x](http://pypy.org/)
-   Install scripts are for [Ubuntu](http://www.ubuntu.com/) (or [Debian](https://www.debian.org/)) but the application should work on any Linux, BSD, or OSX system.
-   Internet Explorer is _NOT_ supported, any compatability with IE is purely coincidental. Please use the latest release of [Firefox](https://www.mozilla.org/en-US/), [Chrome](https://www.google.com/chrome/), [Opera](http://www.opera.com/), or any other browser that supports open standards.

## Questions? Problems? Feature Requests?

[Create an issue](https://github.com/moloch--/RootTheBox/issues) on GitHub if you have any questions, problems or feature requestions. We're happy to help you out with setup/configuration/edits and we're always brainstorming new ideas and looking for cool stuff to add!

## Contributing

We welcome code contributions, please [see our contributing guidelines](https://github.com/moloch--/RootTheBox/blob/master/CONTRIBUTING.md) on the wiki for more information.
