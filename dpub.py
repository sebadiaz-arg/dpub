#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#
# The content of stdin expected by this script must to have these marks:
# "========================" before a Request
# "------------------------" before a Response
# "************************" at the end of file
''' Notes: 
-The data from online sheet is read from second row. The first row is for the title.
-The test cases names must be exactly the same in Postman collection than in the online sheet.
-The online sheet must contain three columns in this order: test cases, requests and responses.
'''

import os
import pickle
import sys
import string
from argparse import ArgumentParser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_TOKEN_PICKLE = 'token.pickle'
#Here you must add the credentials filename you've in the same folder.
_CREDS_FILE = 'drive-credentials.json'
_DOC_ACCESS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
_EXCEL_2007_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


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







def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'spreadsheet', help='The spreadsheet id in Google Drive where publishing')
    parser.add_argument('sheet', help='The sheet where publishing')
    parser.add_argument('cell', help='The first cell where begin publishing, i.e. \'C2\'')
    #parser.add_argument('tests', help='Column letter used for test names, i.e. \'B\'')
    parser.add_argument('-c', '--credentials', help='path to the credentials file',
                        default='./{}'.format(_CREDS_FILE))
    parser.add_argument('-t', '--token', help='path to the access token file',
                        default='./{}'.format(_TOKEN_PICKLE))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    return args



### CORREGIR PARA QUE BUSQUE FRASES COMPLETAS, y no solo palabras
def _find_element_in_list(element, list_element):
    listing=list_element
    try:
        indexPos = listing.index(element)
        return indexPos
    except ValueError:
        return None


def prepareTable(content, onlineSheetRowList, sheetLenght, row):
    ''' We looking for a test case name into the test cases names from the online sheet. 
    Then we get its position into the sheet. '''
    indexPos=None
    key=0
    if sheetLenght > 0:
        newValuesPos=sheetLenght + 2                # It'll indicate the first empty row at the end of the data in the online sheet
    else:
        newValuesPos=_FIRST_ROW_FREE_AFTER_TITLE    # If the sheet is empty, we begin writing in the second row, because the first one is the title

    onlineSheetRowDict={}
    value0=content[0] # test case name
    value1=content[1] # request
    value2=content[2] # response
    for testcase in value0:
      if sheetLenght > 0:   # If online sheet is empty we don't need check if the test case was executed. It wasn't there before.
        indexPos=_find_element_in_list(testcase, onlineSheetRowList)
        #print("PARA FINAL, indexPos:", indexPos)

      dataInDict=[value0[key],value1[key],value2[key]]
      key += 1
      #print("dataInDict:", dataInDict)
      #print(dataInDict)      
      # If the test case name is not in the Online sheet, we'll have indexPos=None
      if indexPos != None:
        indexPosStr=str(indexPos)
        indexPos=int(indexPosStr)
        indexPos += row
        ''' onlineSheetRowDict will have in each position a list with three values: test case name, request and response. 
        The order number is the row position. '''
        onlineSheetRowDict.update({ indexPos: dataInDict })
      elif indexPos == None:   # indexPos only will be None when it is a test case that wasn't in the online sheet
        newValuesPosStr=str(newValuesPos)
        newValuesPos=int(newValuesPosStr)
        onlineSheetRowDict.update({ newValuesPos: dataInDict })
        #print("es NONE!:", onlineSheetRowDict)
        newValuesPos += 1
    
    ''' onlineSheetRowDict has each row position with an array with test case name, request and response. '''
    #print(onlineSheetRowDict)
    return onlineSheetRowDict


def createLastTable(onlineSheetRowDict, newValuesPos):
    ''' onlineSheetRowDict has each row position with an array with test case name, request and response. '''
    value=[]
    values=[]
    empty=[]
    pairDataA=[]
    pairDataB=[]
    pairDataC=[]
    add_test_cases_column=FALSE
    ''' We make a list, in same order than the data in online sheet, with the new requests and responses. 
    The rows that shouldn't be modified will have None content to be skipped. '''
    if newValuesPos == 0:
        newValuesPos=len(onlineSheetRowDict)

### REVISAR ESTE RANGO
    for i in range(_FIRST_ROW_FREE_AFTER_TITLE,100):
        if i in onlineSheetRowDict:
            value=onlineSheetRowDict[i]
            #Inserting test case column if the sheet is empty
            #Inserting request and response
            pairDataA.append(value[0])
            pairDataB.append(value[1])
            pairDataC.append(value[2])
        else:
            pairDataA.append(None)  #Inserting test case column if the sheet is empty
            pairDataB.append(None)
            pairDataC.append(None)

    values.append(pairDataA)
    values.append(pairDataB)
    values.append(pairDataC)
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
    readrange="\'{}\'!{}{}".format(args.sheet,column,row)
    writerange="\'{}\'!{}{}".format(args.sheet,column,row)
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

    '''We get the data from the online sheet, at least from the column with test case names'''
    onlineSheet=_getSheet(args.spreadsheet, readrange, creds)   #Inserting Requests and Responses into spreadsheet
    #print (onlineSheet)
    '''Checking if the online sheet has data or is empty '''
    if 'values' in onlineSheet:
      listTemp=onlineSheet['values']
    else:
      onlineSheet.update({ 'values': [] })
      listTemp=[]

    ''' Moving the test cases names we've got from online sheet towards onlineSheetRowList[] '''
    ''' If the online sheet is empty, then listTemp will be empty so onlineSheetRowList will be empty as well. '''
    ''' listTemp has the test cases we've got from online sheet '''
    key=0
    for i in listTemp[0:]:        
        if len(i) > 0:
            onlineSheetRowList.append(i[0])
        else: 
            onlineSheetRowList.append([])  ### CHECK THIS

        key += 1

    '''Preparing a dictionary with number row order and test case name, and a list with the test case names '''
    sheetLenght=len(onlineSheetRowList)
    onlineSheetRowDict=prepareTable(content, onlineSheetRowList, sheetLenght, row)
    #print(onlineSheetRowDict)
    #print("")
    newValuesPos=sheetLenght
    lastTableToUpload=createLastTable(onlineSheetRowDict, newValuesPos)
    #print("Lasttable!: ", lastTableToUpload)
    _write(args.spreadsheet, writerange, lastTableToUpload, creds)   #Inserting Requests and Responses into spreadsheet


if __name__ == "__main__":
    main()
 