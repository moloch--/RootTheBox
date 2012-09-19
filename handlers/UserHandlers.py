# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch

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
import imghdr
import logging

from uuid import uuid1
from base64 import b64encode, b64decode
from models import User, Team, FileUpload
from mimetypes import guess_type
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler
from BaseHandlers import BaseHandler
from string import ascii_letters, digits
from recaptcha.client import captcha


class HomeHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        user = self.get_current_user()
        self.render('user/home.html', user=user)


class ShareUploadHandler(BaseHandler):
    ''' Handles file shares for teams '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders upload file page '''
        user = self.get_current_user()
        self.render("user/share_view.html", shares=user.team.files)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Shit form validation '''
        user = self.get_current_user()
        try:
            description = self.get_argument("description")
        except:
            self.render("user/error.html",
                        operation="File Upload", errors="Missing description")

        if 0 == len(self.request.files.keys()):
            self.render("user/error.html",
                        operation="File Upload", errors="No file data")
            return

        if 50 * (1024 * 1024) < len(self.request.files['file_data'][0]['body']):
            self.render("user/error.html",
                        operation="File Upload", errors="File too large")
            return
        # Disreguard all user controlled variables
        file_name = os.path.basename(
            self.request.files['file_data'][0]['filename'])
        char_white_list = ascii_letters + digits + "-._"
        file_name = filter(lambda char: char in char_white_list, file_name)
        content = guess_type(file_name)
        if content[0] == None:
            self.render("user/error.html", operation="File Upload",
                        errors="Unknown file content, please zip and upload")
        uuid = str(uuid1())
        filePath = self.application.settings['shares_dir'] + '/' + uuid
        save = open(filePath, 'w')
        data = b64encode(self.request.files['file_data'][0]['body'])
        save.write(data)
        save.close()
        file_upload = FileUpload(
            file_name=unicode(file_name),
            content=unicode(str(content[0])),
            uuid=unicode(uuid),
            description=unicode(description),
            byte_size=len(self.request.files['file_data'][0]['body']),
            team_id=user.team.id
        )
        self.dbsession.add(file_upload)
        self.redirect("/user/shares")


class ShareDownloadHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        try:
            uuid = self.get_argument('uuid')
        except:
            self.render("user/error.html",
                        operation="File Download", errors="Missing parameter")
        user = self.get_current_user()
        share = FileUpload.by_uuid(uuid)
        if share == None or share.team_id != user.team_id:
            self.render("user/error.html",
                        operation="File Download", errors="File does not exist")
        else:
            upload = open(self.application.settings[
                'shares_dir'] + '/' + share.uuid, 'r')
            data = upload.read()
            upload.close()
            self.set_header('Content-Type', share.content)
            self.set_header('Content-Length', share.byte_size)
            self.set_header('Content-Disposition',
                            'attachment; filename=%s' % share.file_name)
            self.write(b64decode(data))
            self.finish()


class SettingsHandler(BaseHandler):
    ''' Does NOT extend BaseUserHandler '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        self.render('user/settings.html', success=None, errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Calls function based on parameter '''
        post_functions = {
            '/avatar': self.post_avatar,
            '/password': self.post_password
        }
        if len(args) == 1 and args[0] in post_functions.keys():
            post_functions[args[0]]()
        else:
            self.render("user/settings.html", success=None, errors=None)

    def post_avatar(self, *args, **kwargs):
        ''' Saves avatar - Reads file header an only allows approved formats '''
        user = User.by_name(self.session.data['name'])
        if self.request.files.has_key('avatar') and len(self.request.files['avatar']) == 1:
            if len(self.request.files['avatar'][0]['body']) < (1024 * 1024):
                if user.avatar == "default_avatar.jpeg":
                    user.avatar = unicode(str(uuid1()))
                elif os.path.exists(self.application.settings['avatar_dir'] + '/' + user.avatar):
                    os.unlink(self.application.
                              settings['avatar_dir'] + '/' + user.avatar)
                ext = imghdr.what(
                    "", h=self.request.files['avatar'][0]['body'])
                if ext in ['png', 'jpeg', 'gif', 'bmp']:
                    user.avatar = user.avatar[:user.
                                              avatar.rfind('.')] + "." + ext
                    file_path = self.application.settings[
                        'avatar_dir'] + '/' + user.avatar
                    avatar = open(file_path, 'wb')
                    avatar.write(self.request.files['avatar'][0]['body'])
                    avatar.close()
                    self.dbsession.add(user)
                    self.dbsession.flush()
                    self.render("user/settings.html",
                                success="Successfully changed avatar", errors=None)
                else:
                    self.render("user/settings.html", success=None,
                                errors=["Invalid image format"])
            else:
                self.render("user/settings.html", success=None,
                            errors=["The image is too large"])
        else:
            self.render("user/settings.html", success=None,
                        errors=["Please provide and image"])

    def post_password(self, *args, **kwargs):
        user = User.by_name(self.session.data['name'])
        form = Form(
            old_password="Please enter your old password",
            new_password="Please enter a new password",
            new_password_two="Please confirm your new password",
        )
        try:
            response = captcha.submit(
                self.get_argument('recaptcha_challenge_field'),
                self.get_argument('recaptcha_response_field'),
                self.application.settings['recaptcha_private_key'],
                self.request.remote_ip
            )
        except:
            self.render("user/settings.html",
                        errors=["Please fill out recaptcha"])
            return
        if self.response.is_valid():
            self.set_password(user, self.get_argument('old_password'),
                              self.get_argument('new_password'),
                              self.get_argument('new_password_two'))
        else:
            self.render("user/settings.html", success=None,
                        errors=["Invalid recaptcha"])

    def set_password(self, user, old_password, new_password, new_password_two):
        ''' Sets a users password '''
        config = ConfigManager.Instance()
        if user.validate_password(old_password):
            if new_password == new_password_two:
                if len(new_password) <= config.max_password_length:
                    user.password = new_password
                    self.dbsession.add(user)
                    self.dbsession.flush()
                    self.redirect("/user/settings.html",
                                  success="Successfully updated password", errors=None)
                else:
                    message = "Password must be less than %d chars" % config.max_password_length
                    self.render(
                        "user/settings.html", success=None, errors=[message])
            else:
                self.render("user/settings.html",
                            success=None, errors=["New password's didn't match"])
        else:
            self.render("user/settings.html", success=None,
                        errors=["Invalid old password"])


class TeamViewHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("user/team.html", teams=Team.get_all())


class TeamAjaxHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Serves team information '''
        try:
            team_id = self.get_argument("team_id")
        except:
            self.render("blank.html")
        team = Team.by_id(team_id)
        if team != None:
            self.render("user/team_ajax.html", team=team)
        else:
            self.render("blank.html")


class ReporterHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("user/reporter.html")
