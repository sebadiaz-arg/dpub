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


def next_cell(cell, majorDimension=drive.ROWS_DIMENSION):
    '''Calculate next cell to read, considering that cell value
    does not include the sheet part'''
    if cell is None:
        raise RefError('Cell to fetch spreadsheet info is None')
    letter, number = split_cell(cell)

    if majorDimension == drive.COLS_DIMENSION:
        number += 1
    elif majorDimension == drive.ROWS_DIMENSION:
        if len(letter) == 1:
            letter = chr(ord(letter) + 1)
        elif len(letter == 2):
            # Consider increasing only last char
            # FIXME Extend this to cover all lenghts of letters
            c = letter[len(letter) - 1]
            c = chr(ord(c) + 1)
            letter = '{}{}'.format(letter[0], c)
        else:
            raise RefError('Invalid column on cell {}'.format(cell))
    else:
        raise RefError('Could not obtain next cell for {}'.format(cell))

    return join_cell(letter, number)


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
