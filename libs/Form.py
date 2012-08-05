# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

@author: hathcox

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


class Form(object):
    ''' Held by FormHandler's to deal with easy validation'''

    def __init__(self, *args, **kwargs):
        self.form_pieces = []
        # Iterate over the dictionary
        for name, message in kwargs.iteritems():
            # if we got supplied with a valid pair
            if type(name) == str and type(message) == str:
                piece = FormPiece(name, message)
                self.form_pieces.append(piece)
            else:
                raise Exception('Forms can only support booleans attached to keyword arguments')

    def __get_piece_names__(self):
        ''' returns peices that are marked with required true '''
        required_pieces = []
        for piece in self.form_pieces:
                required_pieces.append(piece.name)

        return required_pieces

    def __contains_list__(self, small, big):
        ''' checks to make sure that all of the smaller list in inside of the bigger list'''
        all_exist = True
        for item in small:
            if item not in big:
                all_exist = False
        return all_exist

    def __get_piece_by_name__(self, name):
        ''' returns a FormPiece based on name '''
        for piece in self.form_pieces:
            if piece.name == name:
                return piece
        return None

    def set_validation(self, argument_name, error_message):
        ''' Use this to set the argument's error message and type after creating a form '''
        piece = self.__get_piece_by_name__(argument_name)
        # If we have a piece by that name
        if piece != None:
            piece.error_message = error_message

    def __get_error_messages__(self, arguments, required_pieces):
        ''' Returns a list of all applicable error messages '''
        self.errors = []
        print required_pieces
        for piece in required_pieces:
            # If the peice isn't in our argument list
            if piece.name not in arguments.keys():
                self.errors.append(piece.error_message)

    def validate(self, arguments=None):
        ''' This method is used to validate that a form's arguments are actually existant '''
        if arguments != None:
            errors = []
            required_piece_names = self.__get_piece_names__()
            self.__get_error_messages__(arguments, self.form_pieces)
            return len(self.errors) == 0
        return False


class FormPiece():
    ''' This is essentialy a wrapper for a given Input html tag '''

    def __init__(self, name, error_message="Please Fill Out All Forms"):
        ''' name is the argument name, and required is wether or not we care if we got some entry '''
        self.name = name
        self.error_message = error_message
