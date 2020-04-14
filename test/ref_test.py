#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import pytest

from dpub.drive import COLS_DIMENSION, ROWS_DIMENSION
from dpub.ref import (_LAST_COLUMN, _LAST_ROW, RefError,
                      extend_cell_location_to_range, join_cell, join_location,
                      join_range, next_cell, next_col, split_cell,
                      split_location, get_fixed_cell_part)


class TData:
    def __init__(self, args, expected):
        self.args = args
        self.expected = expected


def test_next_cell():

    test_data = [
        TData(['A3'], 'A4'),
        TData(['A3', COLS_DIMENSION], 'A4'),
        TData(['A3', ROWS_DIMENSION], 'B3'),
        TData(['AA3', COLS_DIMENSION], 'AA4'),
        TData(['AA3', ROWS_DIMENSION], 'AB3'),
        TData(['A33', COLS_DIMENSION], 'A34'),
        TData(['A33', ROWS_DIMENSION], 'B33')
    ]

    for d in test_data:
        assert next_cell(*d.args) == d.expected


def test_next_col():
    test_data = [
        ['', 'A'],
        ['A', 'B'],
        ['AA', 'AB'],
        ['CZ', 'DA'],
        ['Z', 'AA'],
        ['AZ', 'BA'],
        ['ZZZZZZ', 'AAAAAAA'],
    ]

    for d in test_data:
        assert next_col(d[0]) == d[1]


def test_split_cell_ok():
    test_data = [
        ['A3', 'A', 3],
        ['F9', 'F', 9],
        ['C1', 'C', 1],
        ['AD3', 'AD', 3],
        ['A3090', 'A', 3090]
    ]

    for d in test_data:
        a, b = split_cell(d[0])
        assert a == d[1]
        assert b == d[2]


def test_split_cell_fails():
    test_data = ['3', 'AA', '', 'F0']

    for d in test_data:
        with pytest.raises(RefError):
            split_cell(d)


def test_split_location():
    test_data = [
        ['location!A3', 'location', 'A3'],
        ['location!F9', 'location', 'F9'],
        ['location!C1', 'location', 'C1'],
        ['location!AD3', 'location', 'AD3'],
        ['location!A3090', 'location', 'A3090'],
        ['A3', None, 'A3'],
        ['F9', None, 'F9'],
        ['C1', None, 'C1'],
        ['AD3', None, 'AD3'],
        ['A3090', None, 'A3090'],
        ['location!', 'location', ''],
        ['whatever', None, 'whatever']
    ]

    for d in test_data:
        a, b = split_location(d[0])
        assert a == d[1]
        assert b == d[2]


def test_join_cell():
    test_data = [
        ['A', '3', 'A3'],
        ['AA', '3', 'AA3'],
        ['A', '33', 'A33'],
    ]

    for d in test_data:
        assert join_cell(d[0], d[1]) == d[2]


def test_join_cell_fails():
    test_data = [
        [None, '3'],
        ['AA', None]
    ]

    for d in test_data:
        with pytest.raises(RefError):
            join_cell(d[0], d[1])


def test_join_location():
    test_data = [
        ['location', 'A3', 'location!A3'],
        ['location', 'AA3', 'location!AA3'],
        ['location', 'A33', 'location!A33']
    ]

    for d in test_data:
        assert join_location(d[0], d[1]) == d[2]


def test_join_location_fails():
    test_data = [
        [None, 'A3'],
        ['location', None]
    ]

    for d in test_data:
        with pytest.raises(RefError):
            join_location(d[0], d[1])


def test_join_range():
    test_data = [
        ['A3', 'C3', 'A3:C3'],
        ['location!A3', 'C3', 'location!A3:C3'],
        ['A1', 'B33', 'A1:B33']
    ]

    for d in test_data:
        assert join_range(d[0], d[1]) == d[2]


def test_join_range_fails():
    test_data = [
        [None, 'A3'],
        ['A3', None]
    ]

    for d in test_data:
        with pytest.raises(RefError):
            join_range(d[0], d[1])


def test_extend_cell_location_to_range():
    test_data = [
        TData(['location!A3'], 'location!A3:{}3'.format(_LAST_COLUMN)),
        TData(['location!A3', COLS_DIMENSION],
              'location!A3:A{}'.format(_LAST_ROW)),
        TData(['location!A3', ROWS_DIMENSION],
              'location!A3:{}3'.format(_LAST_COLUMN))
    ]

    for d in test_data:
        assert extend_cell_location_to_range(*d.args) == d.expected


def test_get_fixed_cell_part():
    test_data = [
        TData(['A3', COLS_DIMENSION], 'A'),
        TData(['A3', ROWS_DIMENSION], 3),
        TData(['A3'], 'A')
    ]

    for d in test_data:
        assert get_fixed_cell_part(*d.args) == d.expected
