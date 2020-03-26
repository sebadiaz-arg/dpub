#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import re

from dpub import drive, parser, pipe, cli

_LAST_ROW = '1001'
_LAST_COLUMN = 'AC'


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
    first_test_id_range = args.tests_first_cell
    first_message_range = args.traces_first_cell

    d = drive.Drive(args.credentials, args.token)
    items = _compose_items()
    tests_map = _read_tests_map(
        d, doc, first_test_id_range, first_message_range, read_dimension, write_dimension)

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
        # Compose the traces or a single test in a single array and print it all at a once
        values = []
        for it in t.items:
            values.append(it.request)
            values.append(it.response)
        _write_trace(d, doc, values, m_range, write_dimension)


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
                    first_test_id_range,
                    first_message_range,
                    read_dimension=drive.COLS_DIMENSION,
                    write_dimension=drive.ROWS_DIMENSION):
    '''Reads the tests ids from the spreadsheet and composes a map
    whose keys are the test ids and the values the range where writting
    the first trace message'''
    m_range = first_message_range
    m_sheet, m_cell = _split_range(m_range)

    t_fullrange = _complete_range(
        first_test_id_range, majorDimension=read_dimension)
    ids = drive.read(doc, t_fullrange, read_dimension)

    tests_map = {}
    for id in ids:
        if id is None or id == '':
            break
        tests_map[id] = Test(id, m_range)

        m_cell = _next_cell(m_cell, read_dimension)
        m_range = _join_range(m_sheet, m_cell)

    return tests_map


def _write_trace(drive, doc, values, range, dimension=drive.ROWS_DIMENSION):
    '''Writes the trace to the indicated range, one message per cell'''
    # TODO COMPLETE the other cases. this first version writes in a
    # cell the request and the next column the response
    drive.write(doc, range, values, dimension)


def _next_cell(cell, majorDimension=drive.ROWS_DIMENSION):
    '''Calculate next cell to read, considering that cell value
    does not include the sheet part'''
    if cell is None:
        raise DPubError('Cell to fetch spreadsheet info is None')
    letter, number = _split_cell(cell)

    if majorDimension == drive.COLS_DIMENSION:
        number += 1
    elif majorDimension == drive.ROWS_DIMENSION:
        if len(letter) == 1:
            letter = chr(ord(letter) + 1)
        elif len(letter == 2):
            # Consider here the last columns AA AB and AC and increase only last char
            c = letter[len(letter) - 1]
            c = chr(ord(c) + 1)
            letter = '{}{}'.format(letter[0], c)
        else:
            raise DPubError('Invalid column on cell {}'.format(cell))
    else:
        raise DPubError('Could not obtain next cell for {}'.format(cell))

    return _join_cell(letter, number)


def _split_cell(cell):
    '''Returns the cell in its letter an number'''
    # Here we split the cell using the decimal part as separator
    # Two first elements belong to column and row
    tokens = re.split(r'(\d+)', cell)
    if len(tokens) < 2:
        raise DPubError('Could not parse cell {}'.format(cell))

    return tokens[0], int(tokens[1])


def _join_cell(letter, number):
    '''Returns the letter and number joined in a cell'''
    return _join(letter, number)


def _split_range(range):
    '''Splits the range in sheet and internal range within the sheet'''
    if range is None:
        raise DPubError('Range is None')

    # If not found the separator, asume that this is only a cell or internal range
    if '!' not in range:
        return None, range

    return range.split('!', 1)


def _join_range(sheet, cell):
    '''Joins a sheet with the cell'''
    return _join(sheet, cell, '!')


def _join_cells(first_cell, last_cell):
    '''Joins a pair of cells to compose an internal range of cells'''
    return _join(first_cell, last_cell, ':')


def _join(a, b, separator=''):
    '''Joins two elements (cells, cell+sheet, etc..) to create a more complex:
    i.e.
    two cells to compose a cells range
    a sheet with a cells range to compose an absolute range reference
    '''
    return '{}{}{}'.format(a, separator, b)


def _complete_range(range, majorDimension=drive.ROWS_DIMENSION):
    '''Completes a range enlarging it to cover all the rest of cells until
    reaching the end of the row or the column'''
    sheet, cell = _split_range(range)
    letter, number = _split_cell(cell)

    if majorDimension == drive.COLS_DIMENSION:
        last_cell = _join_cell(letter, _LAST_ROW)
    elif majorDimension == drive.ROWS_DIMENSION:
        last_cell = _join_cell(_LAST_COLUMN, number)
    else:
        raise DPubError('Wrong dimension when completing a range')

    return _join_range(sheet, '{}:{}'.format(cell, last_cell))
