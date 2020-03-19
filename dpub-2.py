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
'''It's the end of the range, from A1, where we'll get the online sheet to be compared locally after send the updates. Increase if you have a bigger data range in your test plan sheet.'''
_END_RANGE = ':B60'   

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


def _write(document, cell, values, credentials):
    '''Writes certain content to a range in a spreadsheet'''
    service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION,
                    credentials=credentials)

    _validate_cell_ref(cell)

    body = {
        'range': cell,
        'majorDimension': 'COLUMNS',
        #'values': [['',''],['','']] 
        'values': values ### AQUI DEBO MODIFCAR PARA QUE SE CORRAN LAS COLUMNAS EN DONDE UPDATEAR EN FUNCION DE LA COLUMNA INGRESADA EN POR ARGMENTO.
    }

    service.spreadsheets().values().update(
        spreadsheetId=document, range=cell, body=body, valueInputOption='RAW').execute()


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'spreadsheet', help='The spreadsheet id in Google Drive where publishing')
    parser.add_argument('sheet', help='The sheet where publishing')
    parser.add_argument('cell', help='The first cell where begin publishing, i.e. \'C2\'')
    parser.add_argument('tests', help='Column letter used for test names, i.e. \'B\'')
    parser.add_argument('-c', '--credentials', help='path to the credentials file',
                        default='./{}'.format(_CREDS_FILE))
    parser.add_argument('-t', '--token', help='path to the access token file',
                        default='./{}'.format(_TOKEN_PICKLE))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    return args

'''
def _insertOneByOne(listToInsert, listInSheet):
    for listToInsert[0] in line:
        pos=position de line en Lista
        POST lista_a_insertar[1] en posicion correspondiente
'''

def _getSheet(document, range, credentials):
    table=[]
    service = build(_SHEETS_SERVICE, _SHEETS_SERVICE_VERSION,
                    credentials=credentials)
    range = "{}{}".format(range,_END_RANGE)
    getRequest = service.spreadsheets().values().get(spreadsheetId=document, range=range, valueRenderOption='FORMATTED_VALUE')
    table = getRequest.execute()
    return table


def _find_element_in_list(element, list_element):
    listing=list_element
    try:
        indexPos = listing.index(element)
        return indexPos
    except ValueError:
        return None


def prepareTable(content,onlineSheetRowList,newValuesPos):
    key=0
    onlineSheetRowDict={}
    #newValuesPos=len(onlineSheetRowList)
    value0=content[0]
    value1=content[1]
    value2=content[2]    
    for testcase in value0:
      ''' We looking for a test case name into the test cases names from the online sheet. 
         Then we get its position into the sheet. '''
      indexPos=_find_element_in_list(testcase, onlineSheetRowList)
      dataInDict=[value0[key],value1[key],value2[key]]
      key += 1
      # If the test case name is not in the Online sheet, we'll have indexPos=None
      if indexPos != None:
        indexPosStr=str(indexPos)
        indexPos=int(indexPosStr)
        ''' onlineSheetRowDict will have in each position a list with three values: test case name, request and response. 
        The order number is the row position. '''
        onlineSheetRowDict.update({indexPos: dataInDict})
      elif indexPos == None:
        onlineSheetRowDict.update({newValuesPos: dataInDict})
        newValuesPos += 1
    
    return onlineSheetRowDict


def createLastTable(onlineSheetRowDict,newValuesPos):
    values=[]
    empty=[]
    pairDataA=[]
    pairDataB=[]
    # We make a list, in same order than the data in online sheet, with the new requests and responses. Others that shouldn't be modified will be empty
    for i in range(0,newValuesPos):
        if i in onlineSheetRowDict:
            value=onlineSheetRowDict[i]
            #Inserting request and response
            pairDataA.append(value[1])
            pairDataB.append(value[2])
        else:
            pairDataA.append(None)
            pairDataB.append(None)

    ### PARA BORRAR LUEGO!!!!
    #values.append(empty)
    #values.append(empty)
    values.insert(0,empty)
    values.insert(1,empty)
    values.append(pairDataA)
    values.append(pairDataB)
    return values

def main():
    args = _parse_args()
    creds = _lookup_credentials(args.credentials, args.token)
    #row is to follow the row position where we'll insert text into a spreadsheet. 
    #The first insertion will be on row=2, because the first row in the spreadsheet has the titles.
    column=args.cell[0]  #Column letter
    row=int(args.cell[1:])   #Row number
    control=""
    testcase=""
    onlineSheet=[]
    rowAndTest=[]
    onlineSheetRow=[]
    onlineSheetRowList=[]
    listTemp=[]
    onlineSheetRowDict={}
    arresponse=[]
    arrequest=[]
    testjoin=[]
    reqjoin=[]
    resjoin=[]
    content=[]   #An arrays of arrays where content[0] will have the Requests arrays and content[1] the Responses arrays.
    contentTemp=[]
    listNumbers=[]

    #Preparing the info to indicate where begin the location to paste the data into the spreadsheet.
    reqrange="\'{}\'!{}{}".format(args.sheet,column,row)
    # An integer list since 0 to 100 to use after
    # listNumbers=list(range(0,100))
    #We'll read the stdin line by line, putting the Response in one array and the Request in another one. 
    for line in sys.stdin:
     if "========================" not in line and "------------------------" not in line \
       and "************************" not in line and len(line) > 1:  # We check line with content, not empty line
       if "Test case: " in line:
        testcase=(line[11:-2])
        testjoin.append(testcase)
       elif control == "request":
        arrequest.append(line)
       elif control == "response":   
        arresponse.append(line)

     if "************************" in line or "========================" in line:
      control="request"   #We mark to indicate that we've found a Request
      if arrequest != []:
       #We prepare the position to insert the Request and Response into the spreadsheet.
       #After getting a Request and a Response, line by line into an array, we join the content to get a string for each one.
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

    '''We get the data we've in the online sheet, at least in the column with test case names'''
    onlineSheet=_getSheet(args.spreadsheet, reqrange, creds)   #Inserting Requests and Responses into spreadsheet    
    '''Preparing a dictionary with number row order and test case name, and a list with the test case names '''
    listTemp=onlineSheet['values']
    #print(listTemp[0])
    key=0
    for i in listTemp[0:]:
        #onlineSheetRowDict.update( {key : i[0]} )
        onlineSheetRowList.append(i[0])
        key += 1

    newValuesPos=len(onlineSheetRowList)
    onlineSheetRowDict=prepareTable(content,onlineSheetRowList,newValuesPos)
    #print("DICTIONARY: ",onlineSheetRowDict)

    #print(onlineSheet)
    '''We looking for the row number, into the online sheet, of each test case name we're testing''' 
    '''
    # Using for loop 
    for i in onlineSheet: 
        onlineSheetRowList.append(i)
    
    print(onlineSheetRowList)
    '''    

    ''' content[0] has the test cases names we've ran with Newman '''
#    list=content[0]

       # print("Esto es rowAndTest")
        #print(rowAndTest)
    
    lastTableToUpload=createLastTable(onlineSheetRowDict,newValuesPos)
    #print("Lasttable!: ", lastTableToUpload)
    _write(args.spreadsheet, reqrange, lastTableToUpload, creds)   #Inserting Requests and Responses into spreadsheet


if __name__ == "__main__":
    main()
 