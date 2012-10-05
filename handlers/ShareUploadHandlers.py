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
'''


import os

from uuid import uuid4
from base64 import b64encode, b64decode
from models import dbsession, FileUpload
from mimetypes import guess_type
from libs.Form import Form
from libs.Notifier import Notifier
from libs.SecurityDecorators import authenticated
from BaseHandlers import BaseHandler
from string import ascii_letters, digits


class ShareUploadHandler(BaseHandler):
    ''' Handles file shares for teams '''

    MAX_FILE_SIZE = 50 * (1024 * 1024) # 50Mb

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders upload file page '''
        user = self.get_current_user()
        self.render("user/share_files.html", errors=None, shares=user.team.files)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Shit form validation '''
        form = Form(
            description="Please enter a description",
        )
        user = self.get_current_user()
        if form.validate(self.request.arguments):
            user = self.get_current_user()
            if 0 == len(self.request.files.keys()):
                self.render("user/share_files.html", errors=["No file data."], shares=user.team.files)
            elif self.MAX_FILE_SIZE < len(self.request.files['file_data'][0]['body']):
                self.render("user/share_files.html", errors=["File too large."], shares=user.team.files)
            else:
                self.create_file(user)
        else:
            self.render("user/share_files.html", errors=form.errors, shares=user.team.files)

    def create_file(self, user):
        ''' Saves uploaded file '''
        file_name = os.path.basename(self.request.files['file_data'][0]['filename'])
        char_white_list = ascii_letters + digits + "-._"
        file_name = filter(lambda char: char in char_white_list, file_name)
        content = guess_type(file_name)
        if content[0] == None:
            self.render("user/share_files.html", errors=["Unknown file content, please zip and upload"], shares=user.team.files)
        elif len(file_name) < 1:
            self.render("user/share_files.html", errors=["Invalid file name"])
        else:
            uuid = unicode(uuid4())
            filePath = self.application.settings['shares_dir'] + '/' + uuid
            save = open(filePath, 'w')
            data = b64encode(self.request.files['file_data'][0]['body'])
            save.write(data)
            save.close()
            file_upload = FileUpload(
                file_name=unicode(file_name),
                content=unicode(str(content[0])),
                uuid=uuid,
                description=unicode(self.get_argument('description')),
                byte_size=len(self.request.files['file_data'][0]['body']),
                team_id=user.team.id
            )
            dbsession.add(file_upload)
            message = "%s shared %s" % (user.handle, file_name)
            Notifier.team_success(user.team, "File Shared", message)
            self.redirect("/user/share/files")


class ShareDownloadHandler(BaseHandler):
    ''' Download shared files from here '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Get a file and send it to the user '''
        uuid = self.get_argument('uuid', default="", strip=True)
        user = self.get_current_user()
        share = FileUpload.by_uuid(uuid)
        if share == None or share.team_id != user.team_id:
            self.render("user/share_error.html")
        else:
            upload = open(self.application.settings['shares_dir'] + '/' + share.uuid, 'r')
            data = upload.read()
            self.set_header('Content-Type', share.content)
            self.set_header('Content-Length', share.byte_size)
            self.set_header('Content-Disposition', 'attachment; filename=%s' % share.file_name)
            self.write(b64decode(str(data)))  # Send file back to user
            upload.close()
            self.finish()