#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import re

from dpub import cli, drive, output, parser, pipe
from dpub.ref import (extend_cell_location_to_range, join_location, next_cell,
                      split_location)


class DPubError(Exception):
    pass


class Test:
    def __init__(self, id, first_message_range):
        self.id = id
        self.first_message_range = first_message_range
        self.items = []

    def append(self, item):
        '''Appends a test item'''
        self.items.append(item)


def _validate_cell_ref(cell_ref):
    '''Validates that reference to a cell is not a range'''
    if ':' in cell_ref:
        raise DPubError(
            'Only single cells are valid so far: {} is wrong'.format(cell_ref))


# TODO READ AND WRITE DIMENSIONS ARE FIX NOW. Must be addressed later
def run(read_dimension=drive.COLS_DIMENSION,
        write_dimension=drive.ROWS_DIMENSION):
    '''Do it'''
    args = cli.parse_args()
    doc = args.spreadsheet
    first_test_location = args.first_test_location
    first_msg_location = args.first_msg_location
    mode = args.mode

    d = drive.Drive(args.credentials, args.token)
    items = _compose_items()
    tests_map = _read_tests_map(
        d, doc, first_test_location, first_msg_location, read_dimension, write_dimension)

    # Append the items to the tests. If having one profile there will be one
    # trace per profile, but having several, there will be several items
    for it in items:
        if not it.test_id in tests_map:
            # TODO SEE WHAT TO DO HERE WITH THE ERROR MESSAGE
            continue

        t = tests_map[it.test_id]
        t.append(it)

    # For every test, write the related traces
    for _, t in tests_map.items():
        m_range = t.first_message_range
        values = output.compose(t, mode)
        _write_messages(d, doc, values, m_range, write_dimension)


def _compose_items():
    '''Reads input queue and composes the items map. Every item
    is a trace to write for a test'''
    items = []
    q = pipe.to_queue()
    while not q.empty():
        it = parser.parse_item(q)
        # Skip null items, as they are related with completion
        # lines at the end not belonging to any test
        if it:
            items.append(it)
    return items


def _read_tests_map(drive,
                    doc,
                    first_test_location,
                    first_msg_location,
                    read_dimension=drive.COLS_DIMENSION,
                    write_dimension=drive.ROWS_DIMENSION):
    '''Reads the tests ids from the spreadsheet and composes a map
    whose keys are the test ids and the values the range where writting
    the first trace message'''
    m_loc = first_msg_location
    m_sheet, m_cell = split_location(m_loc)

    t_range = extend_cell_location_to_range(
        first_test_location, majorDimension=read_dimension)
    ids = drive.read(doc, t_range, read_dimension)

    tests_map = {}
    for id in ids:
        if id is None or id == '':
            break
        tests_map[id] = Test(id, m_loc)

        m_cell = next_cell(m_cell, read_dimension)
        m_loc = join_location(m_sheet, m_cell)

    return tests_map


def _write_messages(drive, doc, values, range, dimension=drive.ROWS_DIMENSION):
    '''Writes the trace to the indicated range, one message per cell'''
    # TODO COMPLETE the other cases. this first version writes in a
    # cell the request and the next column the response
    drive.write(doc, range, values, dimension)
