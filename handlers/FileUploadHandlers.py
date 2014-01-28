# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch

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

This file conatains handlers related to the file sharing functionality

'''


import os

from models.FileUpload import FileUpload
from libs.SecurityDecorators import authenticated
from BaseHandlers import BaseHandler
from string import printable

MAX_FILE_SIZE = 50 * (1024**2)  # Max file size 50Mb
MAX_UPLOADS = 5


class FileUploadHandler(BaseHandler):
    ''' Handles file shares for teams '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders upload file page '''
        user = self.get_current_user()
        self.render("file_upload/shared_files.html",
            errors=None, shares=user.team.files
        )

    @authenticated
    def post(self, *args, **kwargs):
        ''' Shit form validation '''
        user = self.get_current_user()
        errors = []
        for shared_file in self.request.files['files'][:MAX_UPLOADS]:
            if MAX_FILE_SIZE < len(shared_file['body']):
                errors.append("The file %s is too large")
            else:
                file_upload = self.create_file(user, shared_file)
                event = self.event_manager.create_team_file_share_event(user, file_upload)
                self.new_events.append(event)
        if not len(errors):
            self.redirect("/user/share/files")
        else:
            self.render("file_upload/")

    def create_file(self, user, shared_file):
        ''' Saves uploaded file '''
        file_upload = FileUpload(team_id=user.team.id)
        file_upload.file_name = shared_file['filename']
        file_upload.data = shared_file['body']
        file_upload.description = self.get_argument('description', '')
        self.dbsession.add(file_upload)
        self.dbsession.commit()
        return file_upload


class FileDownloadHandler(BaseHandler):
    ''' Download shared files from here '''

    good_chars = printable[:-38] + '.-_'

    @authenticated
    def get(self, *args, **kwargs):
        ''' Get a file and send it to the user '''
        user = self.get_current_user()
        shared_file = FileUpload.by_uuid(self.get_argument('uuid', ''))
        if shared_file is not None and shared_file in user.team.files:
            self.set_header('Content-Type', shared_file.content_type)
            self.set_header('Content-Length', shared_file.byte_size)
            self.set_header('Content-Disposition', 'attachment; filename=%s' %
                filter(lambda char: char in self.good_chars, shared_file.file_name)
            )
            self.write(shared_file.data)
        else:
            self.render("public/404.html")
