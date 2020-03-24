#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_SHEETS_SERVICE = 'sheets'
_SHEETS_SERVICE_VERSION = 'v4'
'''It's the end of the range, from A1, where we'll get the online sheet to be compared locally after send the updates. Increase if you have a bigger data range in your test plan sheet.'''
_END_RANGE = ':B60'

_FIRST_ROW_FREE_AFTER_TITLE = 2 #ROW 1 has the title
_COL_WITH_TEST_CASES = "A"
FALSE=0
TRUE=1

class PublishToDriveError(Exception):
    pass

def _validate_cell_ref(cell_ref):
    '''Validates that reference to a cell is not a range'''
    if ':' in cell_ref:
        raise PublishToDriveError(
            'Only single cells are valid so far: {} is wrong'.format(cell_ref))


def _read(document, range, credentials):
    table=[]
    service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION, credentials=credentials)
    range = "{}{}".format(range,_END_RANGE)
    getRequest = service.spreadsheets().values().get(spreadsheetId=document, range=range, valueRenderOption='FORMATTED_VALUE')
    table = getRequest.execute()
    return table

def _write(document, cell, values, credentials):
    '''Writes certain content to a range in a spreadsheet'''
    service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION,
                    credentials=credentials)

    _validate_cell_ref(cell)

    body = {
        'range': cell,
        'majorDimension': 'COLUMNS',
        'values': values ### AQUI DEBO MODIFCAR PARA QUE SE CORRAN LAS COLUMNAS EN DONDE UPDATEAR EN FUNCION DE LA COLUMNA INGRESADA EN POR ARGMENTO.
    }

    service.spreadsheets().values().update(
        spreadsheetId=document, range=cell, body=body, valueInputOption='RAW').execute()