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


import logging

from models.FileUpload import FileUpload
from libs.ValidationError import ValidationError
from libs.SecurityDecorators import authenticated
from BaseHandlers import BaseHandler


MAX_UPLOADS = 5


class FileUploadHandler(BaseHandler):

    ''' Handles file shares for teams '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders upload file page '''
        user = self.get_current_user()
        self.render("file_upload/shared_files.html",
                    errors=None,
                    shares=user.team.files)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Shit form validation '''
        user = self.get_current_user()
        self.errors = []
        if hasattr(self.request, 'files'):
            for shared_file in self.request.files['files'][:MAX_UPLOADS]:
                file_upload = self.create_file(user, shared_file)
                if file_upload is not None:
                    self.event_manager.team_file_shared(user, file_upload)
            if not len(self.errors):
                self.redirect("/user/share/files")
            else:
                self.render("file_upload/shared_files.html",
                            errors=self.errors,
                            shares=user.team.files)
        else:
            self.render("file_upload/shared_files.html",
                        errors=["No files in request"],
                        shares=user.team.files)

    def create_file(self, user, shared_file):
        ''' Saves uploaded file '''
        try:
            file_upload = FileUpload(team_id=user.team.id)
            file_upload.file_name = shared_file['filename']
            file_upload.data = shared_file['body']
            file_upload.description = self.get_argument('description', '')
            self.dbsession.add(file_upload)
            self.dbsession.commit()
            return file_upload
        except ValidationError as error:
            self.errors.append(str(error))


class FileDownloadHandler(BaseHandler):

    ''' Download shared files from here '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Get a file and send it to the user '''
        user = self.get_current_user()
        shared_file = FileUpload.by_uuid(self.get_argument('uuid', ''))
        if shared_file is not None and shared_file in user.team.files:
            self.set_header('Content-Type', shared_file.content_type)
            self.set_header('Content-Length', shared_file.byte_size)
            self.set_header('Content-Disposition', 'attachment; filename=%s' % (
                shared_file.file_name))
            self.write(shared_file.data)
        else:
            self.render("public/404.html")


class FileDeleteHandler(BaseHandler):

    ''' Delete shared files '''

    @authenticated
    def post(self, *args, **kwargs):
        user = self.get_current_user()
        shared_file = FileUpload.by_uuid(self.get_argument('uuid', ''))
        if shared_file is not None and shared_file in user.team.files:
            logging.info("%s deleted a shared file %s" % (
                user.handle, shared_file.uuid))
            shared_file.delete_data()
            self.dbsession.delete(shared_file)
            self.dbsession.commit()
            self.redirect('/user/share/files')
        else:
            self.redirect("/404")
