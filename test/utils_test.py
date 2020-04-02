#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from dpub.utils import next_col
import pytest

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

    for t in test_data:
        assert next_col(t[0]) == t[1]
