#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import os
import queue
from enum import Enum

from dpub import utils

_PROFILE_HEADER_KEY = 'Profile:'
_TEST_HEADER_KEY = 'Test:'

_TEST_SIGNATURE_SEP = ' - '

_MARK_SIZE = 30
_END_OF_SECTION_MARK = '-' * _MARK_SIZE
_END_OF_TEST_MARK = '=' * _MARK_SIZE

_SUCCESS_PREFIX = 'Success:'
_FAILURE_PREFIX = 'Fail:'


class ParseError(Exception):
    pass


class Item:
    def __init__(self):
        self.profile = None
        self.test_id = None
        self.test_name = None
        self.request = None
        self.response = None
        self.successful_asserts = None
        self.failed_asserts = None

    def success(self):
        '''Returns true if the item failed asserts is an empty array'''
        return self.failed_asserts is not None and len(self.failed_asserts) == 0


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
    it.successful_asserts, it.failed_asserts = _parse_asserts(q)
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
    while not _is_end_of_section(line):
        if _is_profile_meta_header(line):
            it.profile = _get_profile(line)
        elif _is_test_meta_header(line):
            s = _get_test_signature(line)
            it.test_id, it.test_name = _split_test_signature(s)
        line = _read(q)
    return it


def _parse_request(q):
    '''Returns the parsed request message'''
    return _parse_message(q, _is_end_of_section)


def _parse_response(q):
    '''Returns the parsed response message'''
    return _parse_message(q, _is_end_of_section)


def _parse_asserts(q):
    '''Returns the parsed asserts'''
    oks = []
    fails = []
    line = _read(q)
    while not _is_end_of_test(line):
        if line.startswith(_SUCCESS_PREFIX):
            oks.append(line[len(_SUCCESS_PREFIX):].strip())
        elif line.startswith(_FAILURE_PREFIX):
            fails.append(line[len(_FAILURE_PREFIX):].strip())
        line = _read(q)
    return oks, fails


def _parse_message(q, end_mark_fn):
    '''Returns the parsed message until the end_mark_fn returns true'''
    d = ''
    line = _read(q)
    while not end_mark_fn(line):
        d += line
        line = _read(q)
    return d


def _is_end_of_test(line):
    '''Returns true if the line is the end of the test mark'''
    return _is_separator_line(line, _END_OF_TEST_MARK)


def _is_end_of_section(line):
    '''Returns true if the line is the end of a test section mark'''
    return _is_separator_line(line, _END_OF_SECTION_MARK)


def _is_separator_line(line, mark):
    '''Returns true if reached the end of a section or test, determinated by
    the provided mark'''
    return line.startswith(mark)


def _get_test_signature(test_header):
    '''Returns the test signature in a test header'''
    return _meta_header_value(test_header, _TEST_HEADER_KEY)


def _get_profile(profile_header):
    '''Returns the profile in a profile header removing any existing double quote'''
    p = _meta_header_value(profile_header, _PROFILE_HEADER_KEY)
    return utils.strip_double_quotes(p)


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
        return signature, None

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
