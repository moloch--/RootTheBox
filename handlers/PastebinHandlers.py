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


from handlers.BaseHandlers import BaseHandler
from models.PasteBin import PasteBin
from libs.SecurityDecorators import authenticated


class PasteHandler(BaseHandler):

    ''' Renders the main page '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders the main page for PasteBin '''
        self.render('pastebin/view.html', user=self.get_current_user())


class CreatePasteHandler(BaseHandler):

    ''' Creates paste bin shares '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' AJAX // Display team text shares '''
        self.render('pastebin/create.html', errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Creates a new text share '''
        name = self.get_argument("name", '')
        content = self.get_argument("content", '')
        if 0 < len(name) and 0 < len(content):
            user = self.get_current_user()
            paste = PasteBin(team_id=user.team.id)
            paste.name = name
            paste.contents = content
            self.dbsession.add(paste)
            self.dbsession.commit()
            self.event_manager.team_paste_shared(user, paste)
            self.redirect('/user/share/pastebin')
        else:
            self.render('pastebin/create.html',
                        errors=["Missing name or content"])


class DisplayPasteHandler(BaseHandler):

    ''' Displays shared texts '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' AJAX // Retrieves a paste from the database '''
        paste_uuid = self.get_argument("paste_uuid")
        user = self.get_current_user()
        paste = PasteBin.by_uuid(paste_uuid)
        if paste is None or paste not in user.team.pastes:
            self.render("pastebin/display.html",
                        errors=["Paste does not exist."],
                        paste=None
                        )
        else:
            self.render("pastebin/display.html", errors=None, paste=paste)


class DeletePasteHandler(BaseHandler):

    ''' Deletes shared texts '''

    @authenticated
    def post(self, *args, **kwargs):
        ''' AJAX // Delete a paste object from the database '''
        paste = PasteBin.by_uuid(self.get_argument("uuid", ""))
        user = self.get_current_user()
        if paste is not None and paste in user.team.pastes:
            self.dbsession.delete(paste)
            self.dbsession.commit()
        self.redirect("/user/share/pastebin")
