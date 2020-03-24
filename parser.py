#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from enum import Enum
import queue
import os

_PROFILE_HEADER_KEY = 'Profile:'
_TEST_HEADER_KEY = 'Test:'

_TEST_SIGNATURE_SEP = ' - '

_MARK_SIZE = 30
_END_OF_HEADERS_MARK = '=' * _MARK_SIZE
_END_OF_REQUEST_MARK = '-' * _MARK_SIZE
_END_OF_RESPONSE_MARK = '*' * _MARK_SIZE


class Item:
    def __init__(self):
        self.profile = None
        self.test_id = None
        self.test_name = None
        self.request = None
        self.response = None


def parse_item(q):
    '''Parses next queued lines until having a complete item'''
    it = _parse_headers(q)
    it.request = _parse_request(q)
    it.response = _parse_response(q)
    return it


def _parse_headers(q):
    line = q.get()
    it = Item()
    while not _is_end_of_response(line):
        if _is_profile_header(line):
            it.profile = _get_profile(line)
        elif _is_test_header(line):
            s = _get_test_signature(line)
            it.test_id, it.test_name = _split_test_signature(s)
        line = q.get()
    return it


def _parse_request(q):
    '''Returns the parsed request message'''
    return _parse_message(q, _is_end_of_request)


def _parse_response(q):
    '''Returns the parsed response message'''
    return _parse_message(q, _is_end_of_response)


def _parse_message(q, end_mark_fn):
    '''Returns the parsed message until the end_mark_fn returns true'''
    d = ''
    line = q.get()
    while not end_mark_fn(line):
        d += '{}{}'.format(line, os.linesep)
        line = q.get()
    return d


def _is_end_of_headers(line):
    '''Returns true if the line is the end of the headers section mark'''
    return _is_end_of_section_mark(line, _END_OF_HEADERS_MARK)


def _is_end_of_request(line):
    '''Returns true if the line is the end of the request section mark'''
    return _is_end_of_section_mark(line, _END_OF_REQUEST_MARK)


def _is_end_of_response(line):
    '''Returns true if the line is the end of the response section mark'''
    return _is_end_of_section_mark(line, _END_OF_RESPONSE_MARK)


def _is_end_of_section_mark(line, mark):
    '''Returns true if reached the end of a section, determinated by
    the provided mark'''
    return line.startswith(mark)


def _get_test_signature(test_header):
    '''Returns the test signature in a test header'''
    return _header_value(test_header, _TEST_HEADER_KEY)


def _get_profile(profile_header):
    '''Returns the profile in a profile header'''
    return _header_value(profile_header, _PROFILE_HEADER_KEY)


def _header_value(header, key):
    '''Returns the value of a certain header'''
    if not header:
        return None
    if not key:
        return None
    return header[len(key):].strip()


def _split_test_signature(signature):
    '''Returns the id and name of the test taking the signature
    as parameter

    i.e.

    TL00-01 - Send a message

    is split in

    id: TL00-01
    name: Send a message
    '''
    if not signature:
        return
    # Use '1' as second parameter to indicate that we only desire one split.
    # This ensures that no more splits are done if separator is found more
    # than once
    return signature.split(_TEST_SIGNATURE_SEP, 1)


def _is_test_header(line):
    '''Returns true if line is the test name header'''
    return _is_header(line, _TEST_HEADER_KEY)


def _is_profile_header(line):
    '''Returns true if the line is the profile header'''
    return _is_header(line, _PROFILE_HEADER_KEY)


def _is_header(line, prefix):
    '''Returns true if the line is of the type 
    of the indicated prefix'''
    return line.startswith(prefix)
