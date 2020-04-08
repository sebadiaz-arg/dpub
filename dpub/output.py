#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import os

_CELL_MAX_CHARS = 50000
_PROFILES_SEPARATOR = '-' * 50


class ModeError(Exception):
    def __init__(self, mode):
        super().__init__('Invalid mode: {}'.format(mode))


def compose(test, mode, max=_CELL_MAX_CHARS):
    '''Returns the values to write to the Drive spreadsheet depending
    on the mode

    mode == message -> one message (request or response) per cell
    mode == profile -> one profile per cell
    mode == test -> all messages of a test per cell'''
    values = []

    if mode == 'message':
        # Every message is an element in the values array
        for it in test.items:
            _append(values, it.request, max)
            _append(values, it.response, max)
    elif mode == 'profile':
        # Every profile trace is a value in the values array
        for it in test.items:
            _append(values, _compose_profile_trace(it), max)
    elif mode == 'test':
        # All traces are a single value in the values array
        s = ''
        for it in test.items:
            s += '{}{}'.format(_compose_profile_trace(it),
                               _profile_separator())
        _append(values, s, max)
    else:
        raise ModeError(mode)

    return values


def compose_new_tests(test, mode, max=_CELL_MAX_CHARS):
    '''Returns the values to write to the Drive spreadsheet depending
    on the mode
    mode == message -> one message (request or response) per cell
    mode == profile -> one profile per cell
    mode == test -> all messages of a test per cell'''
    values = []

    if mode == 'message':
        # Every message is an element in the values array
        for it in test.items:
            _append(values, test.id, max)
            _append(values, it.request, max)
            _append(values, it.response, max)
    elif mode == 'profile':
        # Every profile trace is a value in the values array
        for it in test.items:
            _append(values, test.id, max)
            _append(values, _compose_profile_trace(it), max)
    elif mode == 'test':
        # All traces are a single value in the values array
        # TODO: for this mode, the new test ids are not included yet
        s = ''
        for it in test.items:
            s += '{}{}'.format(_compose_profile_trace(it),
                               _profile_separator())
        _append(values, s, max)
    else:
        raise ModeError(mode)

    return values


def _compose_profile_trace(it):
    '''Returns the request and response trace in a string
    for a certain item'''
    return '{}{}{}{}'.format(it.request, os.linesep, os.linesep, it.response)


def _profile_separator():
    '''Returns a fancy profiles string separator, to show several
    profiles traces in the same string in a easy to read way'''
    return '{}{}'.format(_PROFILES_SEPARATOR, os.linesep)


def _append(arr, new_val, max):
    '''Appends a new val to the array, not exceeding the max limit'''
    if arr is None:
        return arr
    arr.append(_trunc(new_val, max))


def _trunc(msg, max):
    '''Truncates the number of chars of a string for not to exceed the max'''
    if len(msg) > max:
        return msg[:_CELL_MAX_CHARS]
    return msg
