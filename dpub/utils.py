#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#


def strip_double_quotes(what):
    '''Strips double quotes from a string'''
    if not what:
        return what

    return what.replace('"', '')
