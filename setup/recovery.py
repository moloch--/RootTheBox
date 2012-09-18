#!/usr/bin/env python
'''
Created on Aug 22, 2012

    Copyright [2012] [Redacted Labs]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


import os
import cmd
import sys
import getpass

from libs.ConsoleColors import *
from libs.ConfigManager import ConfigManager
from models import dbsession, User, Permission


class RecoveryConsole(cmd.Cmd):
    ''' Recovery console for user/passwords '''

    intro = "\n ====================\n" + \
        "   Recovery Console \n" + \
        " ====================\n\n" + \
        "Type 'help' for a list of available commands"
    prompt = underline + "Recovery" + W + " > "

    def do_reset(self, username):
        '''
        Reset a user's password
        Usage: reset <user name>
        '''
        user = User.by_name(username)
        if user == None:
            print(WARN + str("%s user not found in database." % username))
        else:
            sys.stdout.write(PROMPT + "New ")
            sys.stdout.flush()
            user.password = getpass.getpass()
            dbsession.add(user)
            dbsession.flush()
            print(INFO + str(
                "Updated %s password successfully." % user.name))

    def do_ls(self, partial):
        '''
        List all users in the database
        Usage: ls
        '''
        users = User.all()
        for user in users:
            permissions = ""
            if 0 < len(user.permissions_names):
                permissions = " ("
                for perm in user.permissions_names[:-1]:
                    permissions += perm + str(", ")
                permissions += str("%s)" % user.permissions_names[-1])
            print(INFO + user.name + permissions)


    def do_delete(self, username):
        '''
        Delete a user from the database
        Usage: delete <user name>
        '''
        user = User.by_name(username)
        if user == None:
            print(WARN + str("%s user not found in database." % username))
        else:
            username = user.name
            print(WARN + str("Are you sure you want to delete %s?" % username))
            if raw_input(PROMPT + "Delete [y/n]: ").lower() == 'y':
                permissions = Permission.by_user_id(user.id)
                for perm in permissions:
                    print(
                        INFO + "Removing permission: " + perm.permission_name)
                    dbsession.delete(perm)
                dbsession.flush()
                dbsession.delete(user)
                dbsession.flush()
                print(INFO + str(
                    "Successfully deleted %s from database." % username))

    def do_create(self, username):
        '''
        Create a new user account
        Usage: create <user name>
        '''
        user = User(
            name=unicode(username),
        )
        dbsession.add(user)
        dbsession.flush()
        sys.stdout.write(PROMPT + "New ")
        sys.stdout.flush()
        user.password = getpass.getpass()
        dbsession.add(user)
        dbsession.flush()
        print(INFO + "Successfully created, and approved new account.")

    def do_grant(self, username):
        '''
        Add user permissions
        Usage: grant <user name>
        '''
        user = User.by_name(username)
        if user == None:
            print(WARN + str("%s user not found in database." % username))
        else:
            name = raw_input(PROMPT + "Add permission: ")
            permission = Permission(
                permission_name=unicode(name),
                user_id=user.id
            )
            dbsession.add(permission)
            dbsession.add(user)
            dbsession.flush()
            print(INFO + str("Successfully granted %s permissions to %s." %
                             (name, user.name,)))

    def do_strip(self, username):
        '''
        Strip a user of all permissions
        Usage: strip <user name>
        '''
        user = User.by_name(username)
        if user == None:
            print(WARN + str("%s user not found in database." % username))
        else:
            username = user.name
            permissions = Permission.by_user_id(user.id)
            if len(permissions) == 0:
                print(WARN + str("%s has no permissions." % user.name))
            else:
                for perm in permissions:
                    print(
                        INFO + "Removing permission: " + perm.permission_name)
                    dbsession.delete(perm)
            dbsession.flush()
            print(INFO +
                  "Successfully removed %s's permissions." % user.name)

    def do_id(self, user_id):
        '''
        Pull user based on id.
        Usage: id <user_id>
        '''
        print str(User.by_id(user_id))

    def do_exit(self, *args, **kwargs):
        '''
        Exit recovery console
        Usage: exit
        '''
        print(INFO + "Have a nice day!")
        os._exit(0)

    def default(self, command):
        ''' Called when input is not a command '''
        print(WARN + "Unknown command " + bold + command + W + ", see help.")
