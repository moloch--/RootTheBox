# -*- coding: utf-8 -*-
from urllib import quote_plus
from urlparse import parse_qsl

def _form_decode(tuples):
    dict = {}
    for key, value in tuples:
        (curr, _, next) = key.partition('[')
        if next:
            next = ''.join(next.partition(']')[0::2])
            if next:
                dict[curr] = dict.get(curr, [])
                try: dict[curr].append((next, value))
                except: raise Exception('_form_decode: %s target is invalid dict, false array mixin?'%curr)
            else:
                dict[curr] = dict.get(curr, {'#': []})
                try: dict[curr]['#'].append(value)
                except: raise Exception('_form_decode: %s target is invalid array, false dict mixin?'%curr)
        else:
            if not dict.get(curr): dict[curr] = value
            else: raise Exception('_form_decode: %s value already exists. array or object?'%curr)
        
    for key, value in dict.items():
        if type(value).__name__ == 'list': dict[key] = _form_decode(value)
        elif type(value).__name__ == 'dict': dict[key] = value['#']

    return dict
    
def _form_encode(dict):
    list = []
    for key, value in dict.items():
        if type(value).__name__ == 'dict':
            for k, v in _form_encode(value): list.append(['[%s]%s'%(key, k), v])
        elif type(value).__name__ == 'list':
            for v in value: list.append(['[%s][]'%key, v])
        else:
            list.append(['[%s]'%key, value])
    
    return list

# decodes the form/query string into dict. supports nests dicts (key[nested][another]) and arrays (key[]). works well with jQuery.param
form_decode = lambda str: _form_decode(((key, value.decode('utf-8')) for key, value in parse_qsl(str, keep_blank_values=True)))
# encodes a form/query string from a dict. supports nests and arrays
form_encode = lambda dict: str('&'.join(['='.join([quote_plus(''.join(key[1:].partition(']')[0::2])), quote_plus(value.encode('utf-8'))]) for key, value in _form_encode(dict)]))