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


def compose_msgs(test, mode, max=_CELL_MAX_CHARS):
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
        for idx, it in enumerate(test.items):
            s += _compose_profile_trace(it)
            if idx > 0:
                s += _profile_separator()
        _append(values, s, max)
    else:
        raise ModeError(mode)

    return values


def compose_result(test):
    '''Returns the values to write the test result'''
    if not test:
        return None

    if test.success():
        return "OK"
    return "NOK"


def compose_asserts_string(test, include_successful=False):
    '''Returns the result as a string of all failed asserts for
    all the items of a single test, detailing its results and the
    profile it applies if there are more than one.
    Additional, can include the successful asserts as well'''
    asserts = ''
    # Differentiate the profiles only if there's more than one profile
    include_profile = len(test.items) > 1

    for it in test.items:
        if include_profile:
            asserts += '{}:{}'.format(it.profile, os.linesep)

        if include_successful:
            item_asserts = it.successful_asserts + it.failed_asserts
        else:
            item_asserts = it.failed_asserts

        for a in item_asserts:
            # Asserts for this profile have one blank padding when multiprofile
            if include_profile:
                asserts += ' '
            asserts += '{}{}'.format(a, os.linesep)
    return asserts


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
