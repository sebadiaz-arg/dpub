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

_DOC_ACCESS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

_SHEETS_SERVICE = 'sheets'
_SHEETS_SERVICE_VERSION = 'v4'
# '''It's the end of the range, from A1, where we'll get the online sheet to be compared locally after send the updates. Increase if you have a bigger data range in your test plan sheet.'''
# _END_RANGE = ':B60'

# _FIRST_ROW_FREE_AFTER_TITLE = 2 #ROW 1 has the title
# _COL_WITH_TEST_CASES = "A"
# FALSE=0
# TRUE=1

ROWS_DIMENSION = 'ROWS'
COLS_DIMENSION = 'COLUMNS'


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

    def read(self, doc, range, dimension=ROWS_DIMENSION):
        '''Reads a range of data from a spreadsheet'''
        srv = self._service()
        r = srv.spreadsheets().values().get(spreadsheetId=doc, range=range).execute()
        v_table = r.get('values', [])
        
        if v_table is None or len(v_table) == 0:
            return []
        
        if len(v_table) > 1:
            raise ReadFromDriveError('Mismatch size of the values table')
        
        return v_table[0]

    def write(self, doc, range, values, dimension=COLS_DIMENSION):
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


# def _validate_cell_ref(cell_ref):
#     '''Validates that reference to a cell is not a range'''
#     if ':' in cell_ref:
#         raise PublishToDriveError(
#             'Only single cells are valid so far: {} is wrong'.format(cell_ref))


# def _read(document, range, credentials):
#     table=[]
#     service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION, credentials=credentials)
#     range = "{}{}".format(range,_END_RANGE)
#     getRequest = service.spreadsheets().values().get(spreadsheetId=document, range=range, valueRenderOption='FORMATTED_VALUE')
#     table = getRequest.execute()
#     return table

# def _write(document, cell, values, credentials):
#     '''Writes certain content to a range in a spreadsheet'''
#     service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION,
#                     credentials=credentials)

#     _validate_cell_ref(cell)

#     body = {
#         'range': cell,
#         'majorDimension': 'COLUMNS',
#         'values': values ### AQUI DEBO MODIFCAR PARA QUE SE CORRAN LAS COLUMNAS EN DONDE UPDATEAR EN FUNCION DE LA COLUMNA INGRESADA EN POR ARGMENTO.
#     }

#     service.spreadsheets().values().update(
#         spreadsheetId=document, range=cell, body=body, valueInputOption='RAW').execute()


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
