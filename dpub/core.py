#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import re
import os

from dpub import cli, drive, output, parser, pipe
from dpub.ref import (extend_cell_location_to_range, join_location, next_cell,
                      split_location, next_cell_range, prepare_id_range)
from dpub.spinner import Spinner


class DPubError(Exception):
    pass


class Test:
    '''The representation of an executed test and its results per profile. 
    It also includes the representation of where the results must be allocated
    in the final document'''

    def __init__(self, id, first_message_location, result_location=None, asserts_location=None):
        '''Creates an instance of Test'''
        self.id = id
        self.first_message_location = first_message_location
        self.result_location = result_location
        self.asserts_location = asserts_location
        self.items = []

    def append(self, item):
        '''Appends a test item'''
        self.items.append(item)

    def success(self):
        '''Returns true if response of the test was successful
        for all the composing items'''
        for i in self.items:
            if not i.success():
                return False
        return True


def _validate_cell_ref(cell_ref):
    '''Validates that reference to a cell is not a range'''
    if ':' in cell_ref:
        raise DPubError(
            'Only single cells are valid so far: {} is wrong'.format(cell_ref))


# TODO READ AND WRITE DIMENSIONS ARE FIX NOW. Must be addressed later
def run(read_dimension=drive.COLS_DIMENSION,
        write_dimension=drive.ROWS_DIMENSION):
    '''Do it'''
    spinner = Spinner()
    spinner.write('Reading from stdin ... ')

    args = cli.parse_args()
    doc = args.spreadsheet
    first_test_location = args.first_test_location
    first_msg_location = args.first_msg_location
    first_result_location = args.result
    first_asserts_location = args.asserts
    mode = args.mode

    spinner.write('Setup Google Drive access ... ')
    d = drive.Drive(args.credentials, args.token)

    spinner.write('Reading existing tests ... ')
    items = _compose_items()
    last_item_range = ''
    tests_map, last_item_range, ids_not_allowed = _read_tests_map(
        spinner, d, doc, first_test_location, first_msg_location, first_result_location, first_asserts_location, read_dimension, write_dimension)

    ids_to_append = []
    # Append the items to the tests. If having one profile there will be one
    # trace per profile, but having several, there will be several items
    for it in items:
        # For existent test_ids that should't be overwritten
        if it.test_id in ids_not_allowed:
            continue
        # For new test_ids that should be appended at the end of the sheet
        if not it.test_id in tests_map:
            # Here we manage any empty test_id.
            if it.test_id == None:
                it.test_id = "(unknown)"
            # TODO SEE WHAT TO DO HERE WITH THE ERROR MESSAGE
            tests_map[it.test_id] = Test(it.test_id, last_item_range)
            # It's to include the next test_id (if it exist)
            last_item_range = next_cell_range(
                last_item_range, drive.COLS_DIMENSION)
            ids_to_append.append(it.test_id)
        # For existent test_ids with empty data, to be completed
        t = tests_map[it.test_id]
        t.append(it)

    # For every test, write the related traces
    spinner.write('Writing results to spreadsheet ... ')
    for _, t in tests_map.items():
        # Skip tests empty on items, because they can be headers of other tests
        if len(t.items) == 0:
            continue

        spinner.write('Writting test {} ... '.format(t.id))
        m_range = t.first_message_location

        if t.id in ids_to_append:
            # Writing only a new test case id
            values = output.compose_msgs(t, mode, True)
            id_range = prepare_id_range(
                m_range, first_test_location, drive.ROWS_DIMENSION)
            _write_messages(d, doc, values, id_range, write_dimension)
            # Writing only a new test case data
            values = output.compose_msgs(t, mode, False)
            _write_messages(d, doc, values, m_range, write_dimension)
        else:
            values = output.compose_msgs(t, mode, False)
            _write_messages(d, doc, values, m_range, write_dimension)

        if t.result_location:
            res = output.compose_result(t)
            d.write_one(doc, t.result_location, res)

        if t.asserts_location:
            asserts = output.compose_asserts_string(t)
            d.write_one(doc, t.asserts_location, asserts)

    spinner.write('Done.')
    spinner.end()


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


def _read_tests_map(spinner,
                    drive,
                    doc,
                    first_test_location,
                    first_msg_location,
                    first_result_location=None,
                    first_asserts_location=None,
                    read_dimension=drive.COLS_DIMENSION,
                    write_dimension=drive.ROWS_DIMENSION):
    '''Reads the tests ids from the spreadsheet and composes a map
    whose keys are the test ids and the values the range where writing
    the first trace message'''
    r_loc = first_result_location
    if first_result_location:
        r_sheet, r_cell = split_location(r_loc)

    a_loc = first_asserts_location
    if first_asserts_location:
        a_sheet, a_cell = split_location(a_loc)

    m_loc = first_msg_location
    m_sheet, m_cell = split_location(m_loc)

    t_range = extend_cell_location_to_range(
        first_test_location, majorDimension=read_dimension)
    ids = drive.read(doc, t_range, read_dimension)

    # It's m_loc when the spreadsheet is empty.
    last_item_range = m_loc
    tests_map = {}
    ids_not_allowed = []
    for id in ids:
        # Create a test object only if the read test identifier is not empty.
        # Otherwise we are reading an empty row.
        if id and len(id) > 0:
            # Read at m_loc. If m_loc content is not empty at the sheet, skip the
            # test. Only destination empty cells will be written
            if _is_location_empty(drive, doc, m_loc):
                spinner.write('Reading test {} ... '.format(id))
                tests_map[id] = Test(id, m_loc, r_loc, a_loc)
            else:
                ids_not_allowed.append(id)

        # Even for empty rows, increase the cell where writing the output, to
        # Align it with the tests
        m_cell = next_cell(m_cell, read_dimension)
        m_loc = join_location(m_sheet, m_cell)
        last_item_range = m_loc

        if r_loc:
            r_cell = next_cell(r_cell, read_dimension)
            r_loc = join_location(r_sheet, r_cell)

        if a_loc:
            a_cell = next_cell(a_cell, read_dimension)
            a_loc = join_location(a_sheet, a_cell)

    return tests_map, last_item_range, ids_not_allowed


def _is_location_empty(drive, doc, loc):
    '''Returns true if at least the content of the
    first cell of the received location is empty.'''
    dst = drive.read_one(doc, loc)
    return len(dst) == 0


def _write_messages(drive, doc, values, range, dimension=drive.ROWS_DIMENSION):
    '''Writes the trace to the indicated range, one message per cell'''
    # TODO COMPLETE the other cases. this first version writes in a
    # cell the request and the next column the response
    drive.write(doc, range, values, dimension)
