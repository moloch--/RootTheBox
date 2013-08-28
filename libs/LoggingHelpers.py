# -*- coding: utf-8 -*-
'''
Created on Aug 26, 2013

@author: moloch

    Copyright 2013 Root the Box

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


import logging

from libs.Singleton import Singleton
from collections import deque


@Singleton
class ObservableLoggingHandler(logging.StreamHandler):
    '''
    An observable logging class, just shuffles logging messages
    from the main logger to the observers.  A small history is 
    stored in volatile memory. 
    '''

    max_history_size = 100
    _observers = []
    _history = deque()

    def add_observer(self, observer):
        ''' Add new observer and send them any history '''
        if observer not in self._observers:
            self._observers.append(observer)
            observer.update(list(self._history))

    def remove_observer(self, observer):
        ''' Remove ref to an observer '''
        if observer in self._observers:
            self._observers.remove(observer)

    def emit(self, record):
        ''' 
        Overloaded method, gets called when logging messages are sent
        '''
        msg = self.format(record)
        for observer in self._observers:
            observer.update([msg])
        if self.max_history_size < len(self._history):
            self._history.popleft()
        self._history.append(msg)
