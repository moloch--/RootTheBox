# -*- coding: utf-8 -*-
"""
Created on Jun 18, 2018

@author: eljefe

    Copyright 2018 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""

import os
import json
import logging

from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import authenticated
from tornado.options import options
from models.Corporation import Corporation


class MaterialsHandler(BaseHandler):
    @authenticated
    def get(self, *args, **kwargs):
        if self.show_materials():
            subdir = ""
            if len(args) == 1:
                subdir = "/" + args[0] + "/"

            self.render("file_upload/material_files.html", errors=None, subdir=subdir)
        else:
            self.redirect("/gamestatus")

    @authenticated
    def post(self, *args, **kwargs):
        if self.show_materials():
            d = options.game_materials_dir
            if len(args) == 1:
                tmp = os.path.join(os.path.abspath(d), args[0])
                if is_directory_traversal(tmp):
                    logging.warning(
                        "%s attempted to use a directory traversal"
                        % self.request.remote_ip
                    )
                    self.redirect(self.application.settings["forbidden_url"])
                    return
                d = os.path.join(d, args[0])
            self.write(json.dumps(self.path_to_dict(d)))
        else:
            self.redirect("/gamestatus")

    def path_to_dict(self, path):
        d = {"text": os.path.basename(path)}
        if os.path.isdir(path):
            d["type"] = "directory"
            d["children"] = [
                self.path_to_dict(os.path.join(path, x))
                for x in os.listdir(path)
                if x != "README.md"
            ]
        else:
            downloadpath = path.replace(options.game_materials_dir, "/materials")
            downloadpath = downloadpath.replace("\\", "/")
            d["type"] = "file"
            if options.force_download_game_materials:
                d["a_attr"] = {
                    "href": "%s" % downloadpath,
                    "onclick": "window.location.href = '%s';" % downloadpath,
                }
            else:
                d["a_attr"] = {
                    "href": "%s" % downloadpath,
                    "onclick": "window.open('%s');" % downloadpath,
                    "target": "_blank",
                }
            e = os.path.splitext(path)[1][1:]  # get .ext and remove dot
            d["icon"] = "file ext_%s" % e
        return d

    def show_materials(self):
        return (
            self.application.settings["game_started"] or options.game_materials_on_stop
        )


def is_directory_traversal(file_name):
    materials_root_directory = os.path.abspath(options.game_materials_dir)
    requested_path = os.path.abspath(file_name)
    common_prefix = os.path.commonprefix([requested_path, materials_root_directory])
    return common_prefix != materials_root_directory


def has_materials():
    d = options.game_materials_dir
    i = 0
    for f in os.listdir(d):
        if f == "README.md":
            continue
        else:
            i += 1
        return i > 0


def has_box_materials(box):
    if not options.use_box_materials_dir:
        return False

    d = options.game_materials_dir
    path = os.path.join(d, box.name)
    if os.path.isdir(path):
        return box.name
    else:
        corp = Corporation.by_id(box.corporation_id)
        path = os.path.join(d, corp.name, box.name)
    if os.path.isdir(path):
        return os.path.join(corp.name, box.name)
    return False
