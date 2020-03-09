#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#
import os
import pickle
import sys
from argparse import ArgumentParser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_TOKEN_PICKLE = 'token.pickle'
_CREDS_FILE = 'credentials.json'
_DOC_ACCESS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
_EXCEL_2007_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

_SHEETS_SERVICE = 'sheets'
_SHEETS_SERVICE_VERSION = 'v4'

class PublishToDriveError(Exception):
    pass


def _pipe_in():
    msgs = ''
    for line in sys.stdin:
        msgs += line
    return msgs


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


def _validate_cell_ref(cell_ref):
    '''Validates that reference to a cell is not a range'''
    if ':' in cell_ref:
        raise PublishToDriveError(
            'Only single cells are valid so far: {} is wrong'.format(cell_ref))


def _write(document, cell, content, credentials):
    '''Writes certain content to a range in a spreadsheet'''
    service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION,
                    credentials=credentials)

    _validate_cell_ref(cell)

    body = {
        'range': cell,
        'majorDimension': 'ROWS',
        'values': [
            [content],
        ]
    }

    service.spreadsheets().values().update(
        spreadsheetId=document, range=cell, body=body, valueInputOption='RAW').execute()


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'spreadsheet', help='The spreadsheet id in Google Drive where publishing')
    parser.add_argument('sheet_name', help='The sheet where publishing')
    parser.add_argument('column', help='The first column where publishing')
    parser.add_argument('-c', '--credentials', help='path to the credentials file',
                        default='./{}'.format(_CREDS_FILE))
    parser.add_argument('-t', '--token', help='path to the access token file',
                        default='./{}'.format(_TOKEN_PICKLE))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    return args


def main():
    args = _parse_args()
    creds = _lookup_credentials(args.credentials, args.token)
    #msgs = _pipe_in()
    incrange=1
    areq=0
    ares=0
    #column="B"
    control="nada"
    arresponse=[]
    arrequest=[]
    reqjoin=[]
    resjoin=[]
    #sheet_name="Hoja"

    for line in sys.stdin:
     sys.stdout.write(line)
     if "========================" in line:
      control="request"
      incrange += 1
      if incrange > 2:
       columnres=chr(ord(args.column)+1)
       reqrange="\'{}\'!{}{}".format(args.sheet_name,args.column,incrange)
       resrange="\'{}\'!{}{}".format(args.sheet_name,columnres,incrange)
       reqjoin=''.join(arrequest)  #Cambiar guion por salto de linea
       resjoin=''.join(arresponse) #Cambiar guion por salto de linea
       _write(args.spreadsheet, reqrange, reqjoin, creds)
       _write(args.spreadsheet, resrange, resjoin, creds)
       #Reinitializing arrays
       areq=0
       ares=0
       arresponse[:] = []
       arrequest[:] = []
     elif "------------------------" in line:
      control="response"
    
     if control == "request":   
      arrequest.append(line)
      areq += 1
    
     if control == "response":   
      arresponse.append(line)
      ares += 1


if __name__ == "__main__":
    main()
