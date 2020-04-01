#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import sys
from argparse import ArgumentParser

from dpub.drive import CREDS_FILE, TOKEN_PICKLE


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('spreadsheet',
                        help='The spreadsheet id in Google Drive where publishing')
    parser.add_argument('first_test_location',
                        help='The cell where the first test identifier is. i.e. Hoja3!A2')
    parser.add_argument('first_msg_location',
                        help='The cell where the first message of the traces must be written. i.e. Hoja3!D2')
    parser.add_argument('-c', '--credentials', help='path to the credentials file', dest='credentials',
                        default='./{}'.format(CREDS_FILE))
    parser.add_argument('-t', '--token', help='path to the access token file',
                        dest='token', default='./{}'.format(TOKEN_PICKLE))
    parser.add_argument('-m', '--mode',
                        help='mode to write in the spreadsheet. Possible values are \'test\' \'profile\' and \'message\' (default)',
                        dest='mode', default='message')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    return args
