#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from dpub.ref import RefError, split_cell
import pytest


def test_split_cell_ok():
    test_data = [
        ['A3', 'A', 3],
        ['AA3', 'AA', 3],
        ['AC3', 'AC', 3],
    ]

    for d in test_data:
        a, b = split_cell(d[0])
        assert a == d[1]
        assert b == d[2]


def test_split_cell_fails():
    test_data = ['AD3', '3', 'AA', 'A3090', '']
    
    for d in test_data:
        with pytest.raises(RefError):
            split_cell(d)
