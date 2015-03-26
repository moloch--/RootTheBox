# -*- coding: utf-8 -*-
'''
@author: moloch

    Copyright 2014

--------------------------------------------

Check for ticksy .gif and .bmp files
http://jklmnn.de/imagejs/

'''

from string import printable


def is_xss_image(data):
    return all([char in printable for char in data[:16]])
