#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import re

from dpub import drive

_LAST_ROW = '1001'
_LAST_COLUMN = 'Z'


class RefError(Exception):
    pass


def next_cell(cell, majorDimension=drive.COLS_DIMENSION):
    '''Calculate next cell to read, considering that cell value
    does not include the sheet part'''
    if cell is None:
        raise RefError('Cell to fetch spreadsheet info is None')
    letter, number = split_cell(cell)

    if majorDimension == drive.COLS_DIMENSION:
        number = next_row(number)
    elif majorDimension == drive.ROWS_DIMENSION:
        letter = next_col(letter)
    else:
        raise RefError('Could not obtain next cell for {}'.format(cell))

    return join_cell(letter, number)


def next_row(row):
    '''Increases a row in one unit'''
    return row + 1


def next_col(col):
    '''Increases a column in one unit. If the column
    has more than one letters, increses the less weight one.
    If that one is at Z, it will come to A an the next
    weight will be increased.

    i.e.

    A -> B
    AA -> AB
    AZ -> BA
    ZZ -> AAA
    '''
    if col is None:
        return 'A'

    res = []
    carry = True

    for letter in reversed(col):
        if carry:
            if letter.upper() == 'Z':
                next_letter = 'A'
                carry = True
            else:
                next_letter = chr(ord(letter) + 1)
                carry = False
        else:
            next_letter = letter
        res.insert(0, next_letter)

    # In case that carry is still true, we need to
    # prepend a final 'A' letter because we have increased
    # the end of the ZZZ...Z columns and a new letter is needed
    if carry:
        res.insert(0, 'A')

    return ''.join(res)


def prev_cell(cell, majorDimension=drive.ROWS_DIMENSION):
    '''Calculate previous cell to read, considering that cell value
    does not include the sheet part'''

    if cell is None:
        raise RefError('Cell to fetch spreadsheet info is None')

    first_col = 'A'
    first_row = '1'

    letter, number = split_cell(cell)
    if majorDimension == drive.COLS_DIMENSION:
        if number is first_row:
            raise RefError(
                'The row position {} have not a previous one.'.format(first_row))
        else:
            number -= 1
    elif majorDimension == drive.ROWS_DIMENSION:
        if letter is first_col:
            raise RefError(
                'The column position {} have not a previous one.'.format(first_col))
        else:
            letter = prev_col(letter)
    else:
        raise RefError('Could not obtain previous cell for {}'.format(cell))

    return join_cell(letter, number)


def prev_col(col):
    '''Decreases a column in one unit. If the column
    has more than one letters, decreses the less weight one.
    If that one is at A, it will come to Z an the next
    weight will be decreased.

    i.e.

    B -> A
    AB -> AA
    BA -> AZ
    AAA -> ZZ
    '''
    if col is None:
        return 'A'

    first_col = 'A'
    if col is first_col:
        raise RefError(
            '{} column have not a previous column'.format(first_col))

    res = []
    carry = True

    for letter in reversed(col):
        if carry:
            if letter.upper() == 'A':
                prev_letter = 'Z'
                carry = True
            else:
                prev_letter = chr(ord(letter) - 1)
                carry = False
        else:
            prev_letter = letter
        res.insert(0, prev_letter)

    # In case that carry is still true, we need to
    # prepend a final 'A' letter because we have increased
    # the end of the ZZZ...Z columns and a new letter is needed
    if carry:
        res.insert(0, 'Z')

    return ''.join(res)


def split_cell(cell):
    '''Returns the cell in its letter an number'''
    # Here we split the cell using the decimal part as separator
    # Two first elements belong to column and row
    if cell is None:
        raise RefError('Cell is None')

    tokens = re.split(r'(\d+)', cell)
    if len(tokens) < 2:
        raise RefError('Could not parse cell {}'.format(cell))

    letter = tokens[0]
    number = int(tokens[1])

    if not letter:
        raise RefError('Could not find the column')

    if number <= 0:
        raise RefError('Could not find the row')

    return letter, number


def split_location(loc):
    '''Splits the ref location in sheet and internal range within the sheet'''
    if loc is None:
        raise RefError('Reference location is None')

    # If not found the separator, asume that this is only a cell or internal range
    if '!' not in loc:
        return None, loc

    return loc.split('!', 1)


def join_cell(letter, number):
    '''Returns the letter and number joined in a cell'''
    return _join(letter, number)


def join_location(sheet, range):
    '''Joins a sheet with the cell or range'''
    return _join(sheet, range, '!')


def join_range(first_cell, last_cell):
    '''Joins a pair of cells to compose an internal range of cells'''
    return _join(first_cell, last_cell, ':')


def _join(a, b, separator=''):
    '''Joins two elements (cells, cell+sheet, etc..) to create a more complex:
    i.e.
    two cells to compose a cells range
    a sheet with a cells range to compose a location reference
    '''
    if not a or not b:
        raise RefError('Missing required parameter')

    return '{}{}{}'.format(a, separator, b)


def extend_cell_location_to_range(loc, majorDimension=drive.ROWS_DIMENSION):
    '''Completes a cell location enlarging it to cover all the rest of cells until
    reaching the end of the row or the column'''
    # XXX asuming here that parameter is indeed a location cell and not a range
    sheet, cell = split_location(loc)
    letter, number = split_cell(cell)

    if majorDimension == drive.COLS_DIMENSION:
        last_cell = join_cell(letter, _LAST_ROW)
    elif majorDimension == drive.ROWS_DIMENSION:
        last_cell = join_cell(_LAST_COLUMN, number)
    else:
        raise RefError('Wrong dimension when completing a range')

    return join_location(sheet, '{}:{}'.format(cell, last_cell))


def next_cell_range(loc, majorDimension):
    '''Increments the range in one row position in the indicated direction. '''

    if loc is None:
        raise RefError('Cell to fetch spreadsheet info is None')

    sheet, cell = split_location(loc)
    if majorDimension:
        next_cell_value = next_cell(cell, majorDimension)
    else:
        raise RefError('Could not obtain previous cell for {}'.format(cell))

    return join_location(sheet, next_cell_value)


def prev_cell_range(loc, majorDimension):
    '''Decrements the range in one row position in the indicated direction. '''

    if loc is None:
        raise RefError('Cell to fetch spreadsheet info is None')

    sheet, cell = split_location(loc)
    if majorDimension:
        prev_cell_value = prev_cell(cell, majorDimension)
    else:
        raise RefError('Could not obtain previous cell for {}'.format(cell))

    return join_location(sheet, prev_cell_value)


def prepare_id_range(loc, first_test_location, majorDimension=drive.ROWS_DIMENSION):
    ''' Calculates the range to add a new test case id, fusioning 
    the column letter of the first_test_location with the row of current test id. '''

    if loc is None:
        raise RefError('')

    l_sheet, l_cell = split_location(loc)
    l_letter, l_number = split_cell(l_cell)
    f_sheet, f_cell = split_location(first_test_location)
    f_letter, f_number = split_cell(f_cell)

    if majorDimension == drive.ROWS_DIMENSION:
        id_letter = f_letter
        id_number = l_number
    elif majorDimension == drive.COLS_DIMENSION:
        id_letter = l_letter
        id_number = f_number
    else:
        raise RefError('It is not a expected value {}'.format(majorDimension))
    id_cell = join_cell(id_letter, id_number)

    return join_location(l_sheet, id_cell)


def get_fixed_cell_part(cell, dimension=drive.COLS_DIMENSION):
    '''Returns the fixed part of the cell. When
    moving along columns, that will be the row number, when
    moving along rows, that will be the column number'''
    return _get_cell_part(cell, dimension, fixed_part=True)


def get_movable_cell_part(cell, dimension=drive.COLS_DIMENSION):
    '''Returns the movable part of a cell. When moving
    along columns, that is the column. When moving on rows
    that is the row'''
    return _get_cell_part(cell, dimension, fixed_part=False)


def _get_cell_part(cell, dimension, fixed_part):
    '''Returns the fixed or movable part of a cell'''
    if not cell:
        raise RefError('Empty cell')

    if not dimension:
        raise RefError('Empty dimension value')

    if dimension is not drive.COLS_DIMENSION and dimension is not drive.ROWS_DIMENSION:
        raise RefError('Invalid dimension')

    letter, number = split_cell(cell)

    if fixed_part:
        if dimension is drive.COLS_DIMENSION:
            return letter
        return number
    else:
        if dimension is drive.COLS_DIMENSION:
            return number
        return letter


def opposite_dimension(dimension):
    '''Returns the opposite dimension'''
    if not dimension:
        raise RefError('Empty dimension')

    if dimension is not drive.ROWS_DIMENSION and dimension is not drive.COLS_DIMENSION:
        raise RefError('Invalid dimension')

    if dimension == drive.COLS_DIMENSION:
        return drive.ROWS_DIMENSION
    return drive.COLS_DIMENSION
