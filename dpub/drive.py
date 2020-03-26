#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_PICKLE = 'token.pickle'
CREDS_FILE = 'drive-credentials.json'

ROWS_DIMENSION = 'ROWS'
COLS_DIMENSION = 'COLUMNS'

_DOC_ACCESS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

_SHEETS_SERVICE = 'sheets'
_SHEETS_SERVICE_VERSION = 'v4'


class PublishToDriveError(Exception):
    pass


class ReadFromDriveError(Exception):
    pass


class Drive:
    def __init__(self, client_secrets_file=CREDS_FILE, token_pickle_file=TOKEN_PICKLE):
        self.credentials = _lookup_credentials(
            client_secrets_file, token_pickle_file)

    def read_one(self, doc, range):
        '''Returns the first value of a provided range'''
        vals = self.read(doc, range)
        if vals is None or len(vals) == 0:
            return ''
        return vals[0]

    def write_one(self, doc, range, value):
        '''Writes a single value in a single cell'''
        values = [
            value,
        ]
        self.write(doc, range, values)

    def read(self, doc, range, dimension=COLS_DIMENSION):
        '''Reads a range of data from a spreadsheet'''
        srv = self._service()
        r = srv.spreadsheets().values().get(spreadsheetId=doc, range=range).execute()
        v_table = r.get('values', [])
        return _reduce_dimension(v_table)

    def write(self, doc, range, values, dimension=ROWS_DIMENSION):
        '''Writes certain content to a range in a spreadsheet'''
        srv = self._service()
        body = {
            'range': range,
            'majorDimension': dimension,
            'values': [values],
        }
        srv.spreadsheets().values().update(spreadsheetId=doc, range=range,
                                           body=body, valueInputOption='RAW').execute()

    def _service(self):
        return build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION, credentials=self.credentials)


def _reduce_dimension(table):
    '''Reduces the second dimension of a table if not needed.
    i.e.
    [['a'], ['b'], ['c']] is reduced to ['a', 'b', 'c']
    '''
    if table is None:
        return []

    t = []
    for c in table:
        if len(c) == 1:
            t.append(c[0])
        else:
            t.append(c)
    return t


def _lookup_credentials(client_secrets_file, token_pickle_file):
    '''Lookups for token pickle credentials at received path.
    If not found or explired, asks for credentials and saves them
    at the path'''
    creds = None

    if os.path.exists(token_pickle_file):
        with open(token_pickle_file, 'rb') as token:
            creds = pickle.load(token)

    # when no (valid) credentials, let the user log in:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, _DOC_ACCESS_SCOPES)
            creds = flow.run_local_server()

        with open(token_pickle_file, 'wb') as token:
            pickle.dump(creds, token)

    return creds
