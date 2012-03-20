'''
Created on Mar 13, 2012

@author: moloch
'''

import imghdr
import logging

from os import path
from uuid import uuid1
from models import User, FileUpload
from mimetypes import guess_type
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler
from BaseHandlers import UserBaseHandler
from string import ascii_letters, digits
from recaptcha.client import captcha
from libs import Config

class HomeHandler(UserBaseHandler):
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        user = User.by_user_name(self.session.data['user_name'])
        self.render('user/home.html', user = user)

class ShareUploadHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders upload file page '''
        user = self.get_current_user()
        self.render("user/share_view.html", shares = user.team.files)
    
    @authenticated
    def post(self, *args, **kwargs):
        ''' Shit form validation '''
        user = self.get_current_user()
        try:
            description = self.get_argument("description")
        except:
            self.render("user/error.html", operation = "File Upload", errors = "Missing description")

        if not self.request.files.has_key('file_data'):
            self.render("user/error.html", operation = "File Upload", errors = "No file data")

        if 50 * (1024*1024) < len(self.request.files['file_data'][0]['body']):
            self.render("user/error.html", operation = "File Upload", errors = "File too large")

        uuid = str(uuid1())
        filePath = self.application.settings['shares_dir']+'/'+uuid
        save = open(filePath, 'wb')
        save.write(self.request.files['file_data'][0]['body'])
        save.close()
        file_name = path.basename(self.request.files['file_data'][0]['filename'])
        char_white_list = ascii_letters + digits + "-._"
        file_name = filter(lambda char: char in char_white_list, file_name)
        content = guess_type(file_name)
        if content[0] == None:
            self.render("user/error.html", operation = "File Upload", errors = "Unknown file content, please zip and upload")
        file_upload = FileUpload(
            file_name = unicode(file_name),
            content = unicode(str(content[0])),
            uuid = unicode(uuid),
            description = unicode(description),
            byte_size = len(self.request.files['file_data'][0]['body']),
            team_id = user.team.id
        )
        self.dbsession.add(file_upload)
        self.redirect("/user/shares")

class ShareDownloadHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        try:
            uuid = self.get_argument('uuid')
        except:
            self.render("user/error.html", operation = "File Download", errors = "Missing parameter")
        user = self.get_current_user()
        share = FileUpload.by_uuid(uuid)
        if share == None or share.team_id != user.team_id:
            self.render("user/error.html", operation = "File Download", errors = "File does not exist")
        else:
            upload = open(self.application.settings['shares_dir']+'/'+share.uuid, 'rb')
            data = upload.read()
            upload.close()
            self.set_header('Content-Type', share.content)
            self.set_header('Content-Length', share.byte_size)
            self.set_header('Content-Disposition', 'attachment; filename=%s' % share.file_name)
            self.write(data)
            self.finish()

class SettingsHandler(RequestHandler):
    ''' Does NOT extend BaseUserHandler '''
    
    def initialize(self, dbsession):
        ''' Database and URI setup '''
        self.config = Config.Config()
        self.dbsession = dbsession
        self.session_manager = SessionManager.Instance()
        self.session = self.session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        self.post_functions = {
            '/avatar': self.post_avatar,
            '/changepassword': self.post_password
        }
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        user = User.by_user_name(self.session.data['user_name'])
        self.render('user/settings.html', user = user, message = None)
    
    @authenticated
    def post(self, *args, **kwargs):
        ''' Calls function based on parameter '''
        if args[0] in self.post_functions.keys():
            self.post_functions[args[0]](*args, **kwargs)
        else:
            self.render("user/error.html")
    
    def post_avatar(self, *args, **kwargs):
        ''' Saves avatar - Reads file header an only allows approved formats '''
        user = User.by_user_name(self.session.data['user_name'])
        if self.request.files.has_key('avatar') and len(self.request.files['avatar']) == 1:
            if len(self.request.files['avatar'][0]['body']) < (1024*1024):
                if user.avatar == "default_avatar.gif":
                    user.avatar = unicode(str(uuid1()))
                ext = imghdr.what("", h = self.request.files['avatar'][0]['body'])
                if ext in ['png', 'jpeg', 'gif', 'bmp']:
                    user.avatar = user.avatar[:user.avatar.rfind('.')]+"."+ext
                    file_path = self.application.settings['avatar_dir']+'/'+user.avatar
                    avatar = open(file_path, 'wb')
                    avatar.write(self.request.files['avatar'][0]['body'])
                    avatar.close()
                    self.dbsession.add(user)
                    self.dbsession.flush()
                    self.redirect("/user")
                else:
                    self.render("user/error.html", operation = "Uploading avatar", errors = "Invalid image format")
            else:
                self.render("user/error.html", operation = "Uploading avatar", errors = "The image is too large")
        else:
            self.render("user/error.html", operation = "Uploading avatar", errors = "Please provide and image")

    def post_password(self, *args, **kwargs):
        user = User.by_user_name(self.session.data['user_name'])
        try:
            old_password = self.get_argument("old_password")
            new_password = self.get_argument("new_password")
            new_password_two = self.get_argument("new_password2")
        except:
            self.render("user/error.html", operation="Changing Password", errors = "Please fill out all forms!")

        try:
            response = captcha.submit(
                self.get_argument('recaptcha_challenge_field'),
                self.get_argument('recaptcha_response_field'),
                self.config.recaptcha_private_key,
                self.request.remote_ip,)
        except:
            self.render("user/error.html", operation="Changing Password", errors = "Please fill out recaptcha!")
   

        if(user.validate_password(old_password)):
            if(new_password == new_password_two):
                if response.is_valid:
                    user.password = new_password
                    self.dbsession.add(user)
                    self.dbsession.flush()
                    self.render("user/settings.html", message="Succesfully Changed Password!")
                else:
                    self.render("user/error.html", operation="Changing Password", errors = "Invalid Recaptcha!")
            else:
                self.render("user/error.html", operation="Changing Password", errors = "New password's didn't match!")
        else:
            self.render("user/error.html", operation="Changing Password", errors = "Invalid old password!")

class TeamViewHandler(UserBaseHandler):

    def get(self, *args, **kwargs):
        user = self.get_current_user()
        self.render("user/team.html", user = user, team = user.team)        

class LogoutHandler(UserBaseHandler):

    def get(self, *args, **kwargs):
        ''' Clears cookies and session data '''
        self.session_manager.remove_session(self.get_secure_cookie('auth'))
        self.clear_all_cookies()
        self.redirect("/")
