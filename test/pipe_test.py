#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import sys

from dpub import pipe


def test_queue_generation():
    try:
        # Prepare
        lines = []
        n = 10
        for i in range(n):
            lines.append('line{}'.format(i))
        oldstdin = sys.stdin
        sys.stdin = lines

        # Process
        q = pipe.to_queue()

        # Validation
        assert q.empty() == False
        for i in range(n):
            assert q.get() == 'line{}'.format(i)
        assert q.empty() == True

    finally:
        sys.stdin = oldstdin
