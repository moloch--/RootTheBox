# -*- coding: utf-8 -*-
"""
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

This file contains handlers related to the file sharing functionality

"""


import logging

from models.FileUpload import FileUpload
from models.Team import Team
from libs.ValidationError import ValidationError
from libs.SecurityDecorators import authenticated
from .BaseHandlers import BaseHandler
from tornado.options import options
from builtins import str


MAX_UPLOADS = 5


class FileUploadHandler(BaseHandler):

    """Handles file shares for teams"""

    @authenticated
    def get(self, *args, **kwargs):
        if options.team_sharing:
            """Renders upload file page"""
            user = self.get_current_user()
            self.render(
                "file_upload/shared_files.html", errors=None, shares=user.team.files
            )
        else:
            self.redirect("/404")

    @authenticated
    def post(self, *args, **kwargs):
        if options.team_sharing:
            """Shit form validation"""
            user = self.get_current_user()
            self.errors = []
            shares = []
            if user.team:
                shares = user.team.files
            if hasattr(self.request, "files"):
                teams = []
                if user.is_admin():
                    teamval = self.get_argument("team_uuid", "")
                    if teamval == "all":
                        teams = Team.all()
                    elif teamval != "":
                        teams = [Team.by_uuid(teamval)]
                        shares = Team.by_uuid(teamval).files
                else:
                    teams = [user.team]
                for team in teams:
                    for shared_file in self.request.files["files"][:MAX_UPLOADS]:
                        file_upload = self.create_file(team, shared_file)
                        if file_upload is not None:
                            self.event_manager.team_file_shared(user, team, file_upload)
                if not len(self.errors):
                    if user.is_admin():
                        self.redirect("/admin/view/fileshare")
                    else:
                        self.redirect("/user/share/files")
                else:
                    self.render(
                        "file_upload/shared_files.html",
                        errors=self.errors,
                        shares=shares,
                    )
            else:
                self.render(
                    "file_upload/shared_files.html",
                    errors=["No files in request"],
                    shares=shares,
                )
        else:
            self.redirect("/404")

    def create_file(self, team, shared_file):
        if options.team_sharing:
            """Saves uploaded file"""
            try:
                file_upload = FileUpload(team_id=team.id)
                file_upload.file_name = shared_file["filename"]
                file_upload.data = shared_file["body"]
                file_upload.description = self.get_argument("description", "")
                self.dbsession.add(file_upload)
                self.dbsession.commit()
                return file_upload
            except ValidationError as error:
                self.errors.append(str(error))
        else:
            self.redirect("/404")


class FileDownloadHandler(BaseHandler):

    """Download shared files from here"""

    @authenticated
    def get(self, *args, **kwargs):
        if options.team_sharing:
            """Get a file and send it to the user"""
            user = self.get_current_user()
            shared_file = FileUpload.by_uuid(self.get_argument("uuid", ""))
            if user.is_admin() or (
                shared_file is not None and shared_file in user.team.files
            ):
                self.set_header("Content-Type", shared_file.content_type)
                self.set_header("Content-Length", shared_file.byte_size)
                self.set_header(
                    "Content-Disposition",
                    "attachment; filename=%s" % (shared_file.file_name),
                )
                self.write(shared_file.data)
            else:
                self.render("public/404.html")
        else:
            self.redirect("/404")


class FileDeleteHandler(BaseHandler):

    """Delete shared files"""

    @authenticated
    def post(self, *args, **kwargs):
        if options.team_sharing:
            user = self.get_current_user()
            shared_file = FileUpload.by_uuid(self.get_argument("uuid", ""))
            if user.is_admin():
                logging.info(
                    "%s deleted a shared file %s" % (user.handle, shared_file.uuid)
                )
                shared_file.delete_data()
                self.dbsession.delete(shared_file)
                self.dbsession.commit()
                self.redirect("/admin/view/fileshare")
            elif shared_file is not None and shared_file in user.team.files:
                logging.info(
                    "%s deleted a shared file %s" % (user.handle, shared_file.uuid)
                )
                shared_file.delete_data()
                self.dbsession.delete(shared_file)
                self.dbsession.commit()
                self.redirect("/user/share/files")
            else:
                self.redirect("/404")
        else:
            self.redirect("/404")
