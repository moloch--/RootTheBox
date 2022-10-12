#!/usr/bin/env python3
"""
Created on Aug 22, 2012

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
------------------------------------------------------------------------------

The all powerful recovery console

"""
# pylint: disable=unused-wildcard-import


import os
import cmd
import sys
import getpass

from libs.ConsoleColors import *
from builtins import str, input

# We have to import all of the classes to avoid mapper errors
from setup.create_database import *
from models import dbsession


class RecoveryConsole(cmd.Cmd):
    """Recovery console for user/passwords"""

    intro = (
        "\n ====================\n"
        + "   Recovery Console \n"
        + " ====================\n\n"
        + "Type 'help' for a list of available commands"
    )
    prompt = underline + "Recovery" + W + " > "

    def do_chpass(self, username):
        """
        Change a user's password
        Usage: reset <handle>
        """
        user = User.by_handle(username)
        if user is None:
            print(WARN + "'%s' user not found in database." % username)
        else:
            sys.stdout.write(PROMPT + "New ")
            sys.stdout.flush()
            user.password = getpass.getpass()
            dbsession.add(user)
            dbsession.commit()
            print(INFO + "Updated %s password successfully." % user.handle)

    def do_ls(self, obj):
        """
        List all users or teams in the database
        Usage: ls <user/team>
        """
        if obj == "" or obj.lower() == "user" or obj.lower() == "users":
            for user in User.all():
                permissions = ""
                team = ""
                if 0 < len(user.permissions_names):
                    permissions = " ("
                    for perm in user.permissions_names[:-1]:
                        permissions += perm + str(", ")
                    permissions += str("%s)" % user.permissions_names[-1])
                if user.team is not None:
                    team = " from " + bold + str(user.team) + W + " "
                print(INFO + bold + user.handle + W + team + permissions)
        elif obj.lower() == "team" or obj.lower() == "teams":
            for team in Team.all():
                print(
                    INFO
                    + team.name
                    + ": "
                    + ", ".join([user.handle for user in team.members])
                )
        else:
            print(WARN + "Syntax error; see 'help ls'.")

    def do_rmuser(self, username):
        """
        Delete a user from the database
        Usage: delete <handle>
        """
        user = User.by_handle(username)
        if user is None:
            print(WARN + "'%s' user not found in database." % username)
        else:
            username = user.handle
            print(WARN + str("Are you sure you want to delete %s?" % username))
            if input(PROMPT + "Delete [y/n]: ").lower() == "y":
                permissions = Permission.by_user_id(user.id)
                for perm in permissions:
                    print(INFO + "Removing permission: " + perm.name)
                    dbsession.delete(perm)
                dbsession.flush()
                dbsession.delete(user)
                dbsession.commit()
                print(INFO + "Successfully deleted %s from database." % username)

    def do_mkuser(self, nop):
        """
        Make a new user account
        Usage: mkuser
        """
        try:
            user = User(handle=str(input(PROMPT + "Handle: ")))
            dbsession.add(user)
            dbsession.flush()
            sys.stdout.write(PROMPT + "New ")
            sys.stdout.flush()
            user.password = getpass.getpass()
            dbsession.add(user)
            dbsession.commit()
            print(INFO + "Successfully created new account.")
        except:
            print(WARN + "Failed to create new account.")

    def do_mkteam(self, nop):
        """
        Make a new team.
        Usage: mkteam
        """
        try:
            team = Team(
                name=str(input(PROMPT + "Team name: ")),
                motto=str(input(PROMPT + "Team motto: ")),
            )
            dbsession.add(team)
            dbsession.commit()
            print(INFO + "Successfully created new team.")
        except:
            print(WARN + "Failed to create new team.")

    def do_grant(self, username):
        """
        Add user permissions
        Usage: grant <handle>
        """
        user = User.by_handle(username)
        if user is None:
            print(WARN + "'%s' user not found in database." % username)
        else:
            name = input(PROMPT + "Add permission: ")
            permission = Permission(name=str(name), user_id=user.id)
            dbsession.add(permission)
            dbsession.add(user)
            dbsession.commit()
            print(
                INFO
                + "Successfully granted %s permissions to %s." % (name, user.handle)
            )

    def do_strip(self, username):
        """
        Strip a user of all permissions
        Usage: strip <handle>
        """
        user = User.by_handle(username)
        if user is None:
            print(WARN + "'%s' user not found in database." % username)
        else:
            username = user.handle
            permissions = Permission.by_user_id(user.id)
            if len(permissions) == 0:
                print(WARN + "%s has no permissions." % user.handle)
            else:
                for perm in permissions:
                    print(INFO + "Removing permission: " + perm.name)
                    dbsession.delete(perm)
            dbsession.commit()
            print(INFO + "Successfully removed %s's permissions." % user.handle)

    def do_chteam(self, username):
        """
        Change a user's team
        Usage: chteam <handle>
        """
        user = User.by_handle(username)
        if user is None:
            print(WARN + "'%s' user not found in database." % username)
        else:
            print(INFO + "Available teams:")
            for team in Team.all():
                print(" %d. %s" % (team.id, team.name))
            team_id = input(PROMPT + "Set user's team to: ")
            team = Team.by_id(team_id)
            if team is not None:
                user.team_id = team.id
                dbsession.add(user)
                dbsession.commit()
                print(
                    INFO
                    + "Successfully changed %s's team to %s." % (user.handle, team.name)
                )
            else:
                print(WARN + "Team does not exist.")

    def do_id(self, user_id):
        """
        Pull user based on id.
        Usage: id <user_id>
        """
        user = User.by_id(user_id)
        if user is None:
            print(WARN + "'%s' user not found in database." % user_id)
        else:
            print(INFO + repr(user))

    def do_exit(self, *args, **kwargs):
        """
        Exit recovery console
        Usage: exit
        """
        print(INFO + "Have a nice day!")
        os._exit(0)

    def default(self, command):
        """Called when input is not a command"""
        print(WARN + "Unknown command " + bold + command + W + ", see help.")
