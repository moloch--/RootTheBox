# -*- coding: utf-8 -*-
"""
@author: moloch

    Copyright 2013

--------------------------------------------

Custom exception we throw when validating model data

"""


class ValidationError(Exception):

    """Maybe extend this later"""

    def __init__(self, message):
        Exception.__init__(self, message)
