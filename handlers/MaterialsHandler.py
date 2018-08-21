# -*- coding: utf-8 -*-
'''
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

'''

import os
import json

from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import authenticated
from tornado.options import options

class MaterialsHandler(BaseHandler):
    
    @authenticated
    def get(self, *args, **kwargs):
        self.render('file_upload/material_files.html', errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        d=options.game_materials_dir
        self.write(json.dumps(self.path_to_dict(d)))

    def path_to_dict(self, path):
        d = {'text': os.path.basename(path)}
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [self.path_to_dict(os.path.join(path,x)) for x in os.listdir(path) if x != "README.md"]
        else:
            downloadpath = path.replace(options.game_materials_dir, "/materials")
            d['type'] = "file"
            d['a_attr'] = { "href" : "%s" % downloadpath, "onclick":"window.location='%s'" % downloadpath}
            e=os.path.splitext(path)[1][1:] # get .ext and remove dot
            d['icon'] = "file ext_%s" % (e)
        return d

        
def has_materials():
    d=options.game_materials_dir
    i = 0
    for f in os.listdir(d):
        if f == "README.md":
            continue
        else:
            i += 1
    return i > 0