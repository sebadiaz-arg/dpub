#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from dpub.ref import RefError, split_cell
import pytest


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
