"""
Created on Sep 6, 2026

    Copyright 2026 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
----------------------------------------------------------------------------

Shared anti-bruteforce counters. Every code path that validates a password
must go through here, otherwise it becomes an oracle that bypasses the ban
applied on the login form.

"""


import logging

from netaddr import IPAddress


def is_blacklisted(settings, ip_address):
    """Checks whether an ip address is currently banned"""
    return ip_address in settings["blacklisted_ips"]


def reset_failed_logins(settings, ip_address):
    """Clears the failure counter after a successful authentication"""
    settings["failed_logins"].pop(ip_address, None)


def record_failed_login(settings, ip_address):
    """Counts a failed authentication and bans the ip once over threshold"""
    logging.info("*** Failed login attempt from: %s" % ip_address)
    failed_logins = settings["failed_logins"]
    failed_logins[ip_address] = failed_logins.get(ip_address, 0) + 1
    if not settings["automatic_ban"]:
        return
    if failed_logins[ip_address] < settings["blacklist_threshold"]:
        return
    _ban_ip_address(settings, ip_address)


def _ban_ip_address(settings, ip_address):
    """Adds an ip address to the in-memory blacklist"""
    try:
        if IPAddress(ip_address).is_loopback():
            logging.warning("[BAN HAMMER] Cannot blacklist loopback address")
        elif ip_address not in settings["blacklisted_ips"]:
            logging.info("[BAN HAMMER] Automatically banned IP: %s" % ip_address)
            settings["blacklisted_ips"].append(ip_address)
    except:
        logging.exception("Error while attempting to ban ip address")
