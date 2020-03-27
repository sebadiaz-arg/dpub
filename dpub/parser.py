#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import os
import queue
from enum import Enum

_PROFILE_HEADER_KEY = 'Profile:'
_TEST_HEADER_KEY = 'Test:'

_TEST_SIGNATURE_SEP = ' - '

_MARK_SIZE = 30
_END_OF_HEADERS_MARK = '=' * _MARK_SIZE
_END_OF_REQUEST_MARK = '-' * _MARK_SIZE
_END_OF_RESPONSE_MARK = '*' * _MARK_SIZE


class ParseError(Exception):
    pass


class Item:
    def __init__(self):
        self.profile = None
        self.test_id = None
        self.test_name = None
        self.request = None
        self.response = None


def parse_item(q):
    '''Parses next queued lines until having a complete item
    If not able to parse the headers, it returns None'''
    # Return None if not found a first meta header
    first_meta_header = _move_to_first_not_empty_line(q)
    if not first_meta_header:
        return None

    it = _parse_metadata(q, first_meta_header)
    it.request = _parse_request(q)
    it.response = _parse_response(q)
    return it


def _read(q):
    '''Pops element. Raises ParseError if empty'''
    if q.empty():
        raise ParseError('Could not parse trace to item')
    return q.get()


def _move_to_first_not_empty_line(q):
    '''Moves the cursor until reaching the first not empty 
    line. In case of reaching the end, returns None'''
    while True:
        if q.empty():
            return None
        line = q.get()
        if line.strip():
            return line


def _parse_metadata(q, line):
    '''Returns a parse item with the metadata populated'''
    it = Item()
    while not _is_end_of_meta_headers(line):
        if _is_profile_meta_header(line):
            it.profile = _get_profile(line)
        elif _is_test_meta_header(line):
            s = _get_test_signature(line)
            it.test_id, it.test_name = _split_test_signature(s)
        line = _read(q)
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
    line = _read(q)
    while not end_mark_fn(line):
        d += line
        line = _read(q)
    return d


def _is_end_of_meta_headers(line):
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
    return _meta_header_value(test_header, _TEST_HEADER_KEY)


def _get_profile(profile_header):
    '''Returns the profile in a profile header'''
    return _meta_header_value(profile_header, _PROFILE_HEADER_KEY)


def _meta_header_value(header, key):
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
    tokens = signature.split(_TEST_SIGNATURE_SEP, 1)
    if not tokens:
        raise ParseError(
            'Could not split test signature: {}'.format(signature))

    if len(tokens) > 2:
        raise ParseError(
            'Could not split test signature: {}'.format(signature))

    if len(tokens) == 1:
        return signature, signature

    return tokens


def _is_test_meta_header(line):
    '''Returns true if line is the test name header'''
    return _is_meta_header(line, _TEST_HEADER_KEY)


def _is_profile_meta_header(line):
    '''Returns true if the line is the profile header'''
    return _is_meta_header(line, _PROFILE_HEADER_KEY)


def _is_meta_header(line, prefix):
    '''Returns true if the line is of the type 
    of the indicated prefix'''
    return line.startswith(prefix)