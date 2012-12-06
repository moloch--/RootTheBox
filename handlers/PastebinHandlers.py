# -*- coding: utf-8 -*-
'''
Created on Mar 18, 2012

@author: haddaway

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
----------------------------------------------------------------------------

This file contains handlers related to the pastebin functionality

'''

import logging

from handlers.BaseHandlers import BaseHandler
from models import dbsession, User, PasteBin
from libs.Form import Form
from libs.SecurityDecorators import authenticated


class PasteHandler(BaseHandler):
    ''' Renders the main page '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Reners the main page for PasteBin '''
        self.render('pastebin/view.html', user=self.get_current_user())


class CreatePasteHandler(BaseHandler):
    ''' Creates paste bin shares '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' AJAX // Display team text shares '''
        user = self.get_current_user()
        self.render('pastebin/create.html', errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Creates a new text share '''
        form = Form(
            name="Please enter a name",
            content="Please provide some content",
        )
        if form.validate(self.request.arguments):
            user = self.get_current_user()
            paste = PasteBin(
                name=unicode(self.get_argument("name")),
                contents=unicode(self.get_argument("content")),
                team_id=user.team.id
            )
            dbsession.add(paste)
            dbsession.flush()
            self.event_manager.paste_bin(user, paste)
        self.redirect('/user/share/pastebin')


class DisplayPasteHandler(BaseHandler):
    ''' Displays shared texts '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' AJAX // Retrieves a paste from the database '''
        form = Form(
            paste_uuid="Paste does not exist.",
        )
        if form.validate(self.request.arguments):
            paste_uuid = self.get_argument("paste_uuid")
            user = self.get_current_user()
            paste = PasteBin.by_uuid(paste_uuid)
            if paste == None or paste.team_id != user.team.id:
                self.render("pastebin/display.html", errors=["Paste does not exist."], paste=None)
            else:
                self.render("pastebin/display.html", errors=None, paste=paste)
        else:
            self.render("pastebin/display.html", errors=form.errors, paste=None)


class DeletePasteHandler(BaseHandler):
    ''' Deletes shared texts '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' AJAX // Delete a paste object from the database '''
        form = Form(
            paste_uuid="Paste does not exist.",
        )
        if form.validate(self.request.arguments):
            paste_uuid = self.get_argument("paste_uuid")
            paste = PasteBin.by_uuid(paste_uuid)
            user = self.get_current_user()
            if paste != None and paste.team_id == user.team.id:
                dbsession.delete(paste)
                dbsession.flush()
        self.redirect("/user/share/pastebin")
