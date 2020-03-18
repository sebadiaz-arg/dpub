#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#
# The content of stdin expected by this script must to have these marks:
# "========================" before a Request
# "------------------------" before a Response
# "************************" at the end of file

import os
import pickle
import sys
from argparse import ArgumentParser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_TOKEN_PICKLE = 'token.pickle'
#Here you must add the credentials filename you've in the same folder.
_CREDS_FILE = 'drive-credentials.json'
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
        'majorDimension': 'COLUMNS',
        'values': [
            content[0],content[1]
        ]
    }

    service.spreadsheets().values().update(
        spreadsheetId=document, range=cell, body=body, valueInputOption='RAW').execute()


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'spreadsheet', help='The spreadsheet id in Google Drive where publishing')
    parser.add_argument('sheet', help='The sheet where publishing')
    parser.add_argument('cell', help='The first cell where begin publishing, i.e. \'C2\'')
    parser.add_argument('test', help='Column letter used for test names, i.e. \'B\'')
    parser.add_argument('-c', '--credentials', help='path to the credentials file',
                        default='./{}'.format(_CREDS_FILE))
    parser.add_argument('-t', '--token', help='path to the access token file',
                        default='./{}'.format(_TOKEN_PICKLE))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    return args


def insertOneByOne(listToInsert, listInSheet):
    for listToInsert[0] in line:
        pos=position de line en Lista
        POST lista_a_insertar[1] en posicion correspondiente


def main():
    args = _parse_args()
    creds = _lookup_credentials(args.credentials, args.token)
#row is to follow the row position where we'll insert text into a spreadsheet. 
#The first insertion will be on row=2, because the first row in the spreadsheet has the titles.
    column=args.cell[0]  #Column letter
    row=int(args.cell[1:])   #Row number
    control=""
    testcase=""
    arresponse=[]
    arrequest=[]
    testjoin=[]
    reqjoin=[]
    resjoin=[]
    content=[]   #An arrays of arrays where content[0] will have the Requests arrays and content[1] the Responses arrays.

    #Preparing the info to indicate where begin the location to paste the data into the spreadsheet.
    reqrange="\'{}\'!{}{}".format(args.sheet,column,row)
    #We'll read the stdin line by line, putting the Response in one array and the Request in another one. 
    for line in sys.stdin:
     if "========================" not in line and "------------------------" not in line and "************************" not in line:
       if "Test case: " in line:
        testcase=(line[11:])
       elif control == "request":
        arrequest.append(line)
       elif control == "response":   
        arresponse.append(line)

     if "************************" in line or "========================" in line:
      control="request"   #We've found a Request
      if arrequest != []:
       #We prepare the position to insert the Request and Response into the spreadsheet.
       #After getting a Request and a Response, line by line into an array, we join the content to get a string for each one.
       testjoin.append(testcase)
       reqjoin.append(''.join(arrequest))
       resjoin.append(''.join(arresponse))
       #Reinitializing arrays to retrieve the next Requests/Responses.
       arresponse[:] = []
       arrequest[:] = []

     elif "------------------------" in line:
      control="response"   #We've found a Response

    content.append(testjoin)  #Inserting the array with the test case names in content[0]
    content.append(reqjoin)   #Inserting the array with the requests in content[1]
    content.append(resjoin)   #Inserting the array with the responses in content[2]
    _write(args.spreadsheet, reqrange, content, creds)   #Inserting Requests and Responses into spreadsheet

if __name__ == "__main__":
    main()
