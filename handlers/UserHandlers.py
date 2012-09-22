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

from uuid import uuid4
from base64 import b64encode, b64decode
from models import dbsession, User, Team, FileUpload, Theme
from mimetypes import guess_type
from libs.Form import Form
from libs.Notifier import Notifier
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
            elif 50 * (1024 * 1024) < len(self.request.files['file_data'][0]['body']):
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
            upload = open(self.application.settings['shares_dir'] + '/' + share.uuid, 'r')
            data = upload.read()
            self.set_header('Content-Type', share.content)
            self.set_header('Content-Length', share.byte_size)
            self.set_header('Content-Disposition', 'attachment; filename=%s' % share.file_name)
            self.write(b64decode(data))  # Send file back to user
            upload.close()
            self.finish()


class SettingsHandler(BaseHandler):
    ''' Does NOT extend BaseUserHandler '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        self.render_page()

    @authenticated
    def post(self, *args, **kwargs):
        ''' Calls function based on parameter '''
        post_functions = {
            '/avatar': self.post_avatar,
            '/password': self.post_password,
            '/theme': self.post_theme,
        }
        if len(args) == 1 and args[0] in post_functions.keys():
            post_functions[args[0]]()
        else:
            self.render_page()

    def render_page(self, errors=None, success=None):
        ''' Small wrap for self.render to cut down on lenghty params '''
        current_theme = Theme.by_cssfile(self.session["theme"])
        self.render("user/settings.html", errors=errors, success=success, current_theme=current_theme)

    def post_avatar(self, *args, **kwargs):
        ''' Saves avatar - Reads file header an only allows approved formats '''
        user = User.by_id(self.session['user_id'])
        if self.request.files.has_key('avatar') and len(self.request.files['avatar']) == 1:
            if len(self.request.files['avatar'][0]['body']) < (1024 * 1024):
                if user.avatar == "default_avatar.jpeg":
                    user.avatar = unicode(uuid4())
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
                    dbsession.add(user)
                    dbsession.flush()
                    self.render_page(success=["Successfully changed avatar"])
                else:
                    self.render_page(errors=["Invalid image format"])
            else:
                self.render_page(errors=["The image is too large"])
        else:
            self.render_page(errors=["Please provide and image"])

    def post_password(self, *args, **kwargs):
        ''' Called on POST request for password change '''
        user = User.by_name(self.session.data['name'])
        form = Form(
            old_password="Please enter your old password",
            new_password="Please enter a new password",
            new_password_two="Please confirm your new password",
            recaptcha_challenge_field="Please solve the captcha",
            recaptcha_response_field="Please solve the captcha",
        )
        if self.check_recaptcha():
            self.set_password(user, self.get_argument('old_password'),
                              self.get_argument('new_password'),
                              self.get_argument('new_password_two'))
        else:
            self.render_page(errors=["Invalid recaptcha"])

    def post_theme(self, *args, **kwargs):
        ''' Change per-user theme '''
        form = Form(
            theme_uuid="Please select a theme",
        )
        if form.validate(self.request.arguments):
            theme = Theme.by_uuid(self.get_argument('theme_uuid'))
            if theme != None:
                self.session['theme'] = ''.join(theme.cssfile)
                self.session.save()
                user = self.get_current_user()
                user.theme_id = theme.id
                dbsession.add(user)
                dbsession.flush()
                self.render_page()
            else:
                self.render_page(errors=["Theme does not exist."])
        else:
            self.render_page(errors=form.errors)

    def set_password(self, user, old_password, new_password, new_password_two):
        ''' Sets a users password '''
        config = ConfigManager.Instance()
        if user.validate_password(old_password):
            if new_password == new_password_two:
                if len(new_password) <= config.max_password_length:
                    user.password = new_password
                    dbsession.add(user)
                    dbsession.flush()
                    self.render_page(success=["Successfully updated password"])
                else:
                    message = "Password must be less than %d chars" % config.max_password_length
                    self.render_page(errors=[message])
            else:
                self.render_page(errors=["New password's didn't match"])
        else:
            self.render_page(errors=["Invalid old password"])

    def check_recaptcha(self):
        ''' Checks recaptcha '''
        if self.config.recaptcha_enable:
            response = None
            try:
                response = captcha.submit(
                    self.get_argument('recaptcha_challenge_field'),
                    self.get_argument('recaptcha_response_field'),
                    self.config.recaptcha_private_key,
                    self.request.remote_ip
                )
            except:
                logging.exception("Recaptcha API called failed.")
            if response != None and response.is_valid:
                return True
            else:
                return False
        else:
            return True

class ReporterHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("user/reporter.html")
