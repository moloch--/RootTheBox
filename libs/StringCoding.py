# -*- coding: utf-8 -*-
"""
Created on Jul 14, 2018

@author: eljeffe

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
# pylint: disable=unused-variable


from base64 import b64encode, b64decode
import codecs
import sys


def encode(s, name="utf-8", *args, **kwargs):
    if name == "base64":
        if isinstance(s, str):
            try:
                s = bytearray(s, "utf-8")
            except:
                pass
        return b64encode(s).decode("utf-8").strip()
    if isinstance(s, (bytes, bytearray)):
        # requires str, already encoded?
        return s
    codec = codecs.lookup(name)
    rv, length = codec.encode(s, *args, **kwargs)
    if not isinstance(rv, (str, bytes, bytearray)):
        raise TypeError("Not a string or byte codec")
    return rv


def decode(s, name="utf-8", *args, **kwargs):
    if name == "base64":
        try:
            return bytearray(b64decode(s)).decode("utf-8")
        except:
            pass
    if isinstance(s, str):
        # requires bytes, already decoded?
        return s
    codec = codecs.lookup(name)
    rv, length = codec.decode(s, *args, **kwargs)
    if not isinstance(rv, (str, bytes, bytearray)):
        raise TypeError("Not a string or byte codec: type %s" % type(rv))
    return rv


def unicode(s, name="utf-8", *args, **kwargs):
    # used in python2 to return a unicode type from string
    codec = codecs.lookup(name)
    rv, length = codec.decode(s, *args, **kwargs)
    return rv


def set_type(value, basevalue):
    # try to set value to basevalue type
    basetype = type(basevalue)
    if type(value) == basetype:
        return value
    elif isinstance(basevalue, bool):
        if str(value).upper() == "TRUE":
            return True
        else:
            return False
    elif isinstance(basevalue, int):
        return int(value)
    elif type(unicode(value)) == basetype:
        return unicode(value)
    elif type(str(value)) == basetype:
        return str(value)
    elif type(bytes(value)) == basetype:
        return bytes(value)
    return value
