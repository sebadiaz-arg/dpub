#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import sys
from queue import Queue


def to_queue():
    '''Read the pipe in and store lines as queue elements'''
    q = Queue()
    for line in sys.stdin:
        q.put(line)
    return q
