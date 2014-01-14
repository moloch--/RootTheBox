# -*- coding: utf-8 -*-
'''
@author: moloch

    Copyright 2013

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


from threading import Lock


class Singleton(object):
    ''' Thread safe singleton '''

    def __init__(self, decorated):
        self._decorated = decorated
        self._instance_lock = Lock()

    def instance(self):
        '''
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        '''
        if not hasattr(self, "_instance"):
            with self._instance_lock:
                if not hasattr(self, "_instance"):
                    self._instance = self._decorated()
        return self._instance


    def __call__(self):
        raise TypeError(
            'Singletons must be accessed through the `instance` method.'
        )
