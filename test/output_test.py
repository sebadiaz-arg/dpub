#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from dpub.output import compose_msgs, ModeError
# Renaming required for not pytest drive crazy with the 'Test' name
from dpub.core import Test as T
from dpub.parser import Item
import pytest


def test_compose_output():
    # Prepare
    t = T('id', 'Test!A1')
    n = 10
    for i in range(n):
        it = Item()
        it.request = _the_request(i)
        it.response = _the_response(i)
        t.append(it)

    # Process 'message' mode
    values = compose_msgs(t, 'message')

    # Validate
    assert len(values) == n*2
    i = 0
    for it in t.items:
        assert it.request == values[i]
        i += 1
        assert it.response == values[i]
        i += 1

    # Process 'profile' mode
    values = compose_msgs(t, 'profile')

    # Validate
    assert len(values) == n
    i = 0
    for it in t.items:
        assert it.request in values[i]
        assert it.response in values[i]
        i += 1

    # Process 'test' mode
    values = compose_msgs(t, 'test')

    # Validate
    assert len(values) == 1
    for it in t.items:
        assert it.request in values[0]
        assert it.response in values[0]

    # Validate 'invalid' mode
    with pytest.raises(ModeError):
        compose_msgs(t, 'invalid')


def _the_request(i):
    return 'The request {}'.format(i)


def _the_response(i):
    return 'The response {}'.format(i)
