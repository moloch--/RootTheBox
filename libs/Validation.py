# -*- coding: utf-8 -*-
'''
Created on Aug 27, 2013

@author: lavalamp
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

import imghdr

#TODO make sure this validation encompasses everything necessary...
def validate_avatar_file(requestFileObject):
    errors = []
    ext = imghdr.what("", requestFileObject[0]['body'])
    if len(requestFileObject[0]['body']) > (1024 * 1024):
        errors.append("The image is too large")
    if ext not in ['png', 'jpeg', 'gif', 'bmp']:
        errors.append("Invalid image format, avatar must be: .png .jpeg .gif or .bmp")
    return errors
