#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from dpub.drive import _reduce_dimension


def test_reduce_dimension():
    test_data = [
        # Test 1
        [
            [['a'], ['b'], ['c']],
            ['a', 'b', 'c']
        ],
        # Test 2
        [
            [['a'], [''], ['c']],
            ['a', '', 'c']
        ],
        # Test 3
        [
            [[]],
            ['']
        ],
        # Test 4
        [
            [['a', 'b'], ['c']],
            [['a', 'b'], ['c']]
        ]
    ]

    for t in test_data:
        assert _reduce_dimension(t[0]) == t[1]
