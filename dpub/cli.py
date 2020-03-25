#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import sys
from argparse import ArgumentParser
from dpub.drive import CREDS_FILE, TOKEN_PICKLE


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('spreadsheet', help='The spreadsheet id in Google Drive where publishing')
    parser.add_argument('tests_first_cell', help='The cell where the first test identifier is. i.e. Hoja3!A2')
    parser.add_argument('traces_first_cell', help='The cell where the first trace must be written. i.e. Hoja3!D2')
    parser.add_argument('-c', '--credentials', help='path to the credentials file', dest='credentials',
                        default='./{}'.format(CREDS_FILE))
    parser.add_argument('-t', '--token', help='path to the access token file', dest='token',
                        default='./{}'.format(TOKEN_PICKLE))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    return args
