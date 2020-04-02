#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#


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
