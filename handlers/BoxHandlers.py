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

from models.Box import Box
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler  # @UnresolvedImport


class BoxesViewHandler(RequestHandler):

    def initialize(self, dbsession):
        self.dbsession = dbsession

    @authenticated
    def get(self, *args, **kwargs):
        self.render("boxes/view.html", boxes=Box.get_all())
