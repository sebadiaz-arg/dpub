#!/usr/bin/env python3
#
# Copyright (C) 2020 Telefónica S.A. All Rights Reserved
#

from dpub import parser
from queue import Queue

trace = '''

Profile: +447521168738
Test: 01-01 - Request User Profile
================================================================
POST /product-management/v1/users/me/orders/unsubscribe HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJraWQiOiI0ZjI0MzM3NTI2NThmYTBjMTg4ZDM2MTdmNmNjNDY5ZjQ5NzJiOWYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyMDAwMDAwMDAwMDAwMDE2NTQ0OCIsImF1dGhvcml6YXRpb25faWQiOiJjNGJlMmQ4NC1jM2M5LTRhZjQtOGI4Yi03YjM4Y2M0YThiYWQiLCJwdXJwb3NlIjoiaWRlbnRpZnktY3VzdG9tZXIgY3VzdG9tZXItc2VsZi1zZXJ2aWNlIiwiaXNzIjoiaHR0cHM6XC9cL2F1dGgudWstY2VydDAuYmFpa2FscGxhdGZvcm0uY29tXC8iLCJhdXRoZW50aWNhdGlvbl9jb250ZXh0IjpbeyJpZGVudGlmaWVyIjoidGVzdDkxOTY1MjA4QHN0Zi5yZWYubzIuY28udWsiLCJ0eXBlIjoiZW1haWwifV0sImFjdGl2ZSI6dHJ1ZSwiY2xpZW50X2lkIjoibm92dW0tbXl0ZWxjbyIsImlkZW50aWZpZXJfYm91bmRfc2NvcGUiOltdLCJhdWQiOiJodHRwczpcL1wvYXBpLnVrLWNlcnQwLmJhaWthbHBsYXRmb3JtLmNvbSIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3Mgb3BlbmlkIGV2ZW50LWxvdy1kYXRhLXJlYWQgdXNlcnByb2ZpbGUtcmVhZCBhdXJhaWQtcmVhZCBteW8ybWlkZGxld2FyZS1yZWFkIHdlYnZpZXdzLXBob25lLW51bWJlci1yZWFkIGV2ZW50LXN1YnNjcmlwdGlvbi10eXBlLW1pZ3JhdGlvbi1yZWFkIGF1dGhlbnRpY2F0aW9uLWluZm9ybWF0aW9uLXJlYWQgZXZlbnQtbG93LXZvaWNlLXJlYWQgd2Vidmlld3MtdXNlci1yZWFkIHByb2R1Y3QtbWFuYWdlbWVudC1vcmRlcnMtdXNlci1yZWFkIGV2ZW50LWJhci1hbGVydC1yZWFkIGV2ZW50LW5vLWRhdGEtcmVhZCBleHBsb3JlLWNvbnRlbnQtY2FyZC1kZXRhaWxzLXBob25lLW51bWJlci1yZWFkIHN1YnNjcmliZWQtcHJvZHVjdHMtcmVhZCBtb2JpbGUtYmFsYW5jZS1yZWFkIGV2ZW50LW5vLWJhbGFuY2UtcmVhZCBzdWJzY3JpYmVkLXByb2R1Y3RzLXVzZXItcmVhZCBpbnZvaWNpbmctcGhvbmUtbnVtYmVyLXJlYWQgZXZlbnQtYXBwb2ludG1lbnQtcmVtaW5kZXItcmVhZCBldmVudC1pbnZvaWNlLWRlYml0LXJlYWQgZXZlbnQtcGF5bWVudC1hbGVydC1yZWFkIG15bzJtaWRkbGV3YXJlLXdyaXRlIGF1cmFpZC13cml0ZSBtb2JpbGUtcXVvdGEtcmVhZCBzdWJzY3JpYmVkLXByb2R1Y3RzLXBob25lLW51bWJlci1yZWFkIGV2ZW50LW5vLXZvaWNlLXJlYWQgbm90aWZpY2F0aW9ucy1yZWFkIGV2ZW50LWhpZ2gtc3BlbmQtYWxlcnQtcmVhZCB0aW1lbGluZS1yZWFkIHByb2R1Y3QtbWFuYWdlbWVudC1vcmRlcnMtdXNlci13cml0ZSBldmVudC1kaXNjb25uZWN0aW9uLWFsZXJ0LXJlYWQgZXZlbnQtaW52b2ljZS1wYXltZW50LWR1ZS1yZWFkIG1vYmlsZS1iYWxhbmNlLXRvcC11cC13cml0ZSBpbnZvaWNpbmctdXNlci1yZWFkIGV2ZW50LWxvdy1iYWxhbmNlLXJlYWQgcHJvZHVjdC1tYW5hZ2VtZW50LW9yZGVycy1waG9uZS1udW1iZXItd3JpdGUgZXhwbG9yZS1jb250ZW50LW1vZHVsZXMtdXNlci1yZWFkIGlzc3Vlcy1jcmVhdGUgZXhwbG9yZS1jb250ZW50LWNhcmQtZGV0YWlscy11c2VyLXJlYWQgbW9iaWxlLWJhbGFuY2UtdG9wLXVwLXJlYWQgaW52b2ljaW5nLXJlYWQgZXZlbnQtaW52b2ljZS1yZXRhaW5lZC1yZWFkIGV4cGxvcmUtY29udGVudC1tb2R1bGVzLXBob25lLW51bWJlci1yZWFkIHByb2R1Y3QtbWFuYWdlbWVudC1vcmRlcnMtcGhvbmUtbnVtYmVyLXJlYWQgaXNzdWVzLXJlYWQgZXZlbnQtaW52b2ljZS1jaGFyZ2UtcmVhZCIsImFjcl92YWx1ZXMiOiIzIiwiZXhwIjoxNTg0NzIyMzEyLCJpYXQiOjE1ODQ3MTg3MTIsImp0aSI6IjU0OWY5NGY5LWQwNGItNDAxNC05MzUyLTBhOGZhNTI3ODI1MSJ9.ULKQ3FnZ-8bONmiBkBKsK-4waxsmjU_ieegEaPNsA6jwJqYprC2qab0wEbaT1ZtqBA0KhLViZo0qhNFNZJdfWd0hTDcL3Q_2TJ953UcF0ylLnA1DfraZkiEw7LVBxdRoi4zUI9r_kiryczSEVxd0-6ZUWQeW38XaZ_x4hb9FtCy6RS06KrG1VYCpJN-kEyw054ptiNsIgymjpcfRjx9WPsS_TLbCQg-rBLDZX-Fy0Qh4J-1FzO61VHfIuzO6SZwAP0DlduPhxQ8xSBusYp9MR5jvhtmaFTQQZritKaq9wjdvw7IDFEDB_PuEeBsIAoXwKorP1G5TNbJhTf_pq07dfg
User-Agent: PostmanRuntime/7.22.0
Accept: */*
Cache-Control: no-cache
Postman-Token: e189ab0d-1905-4930-a5af-991feb575eda
Host: api.uk-cert0.baikalplatform.com
Accept-Encoding: gzip, deflate, br
Content-Length: 34
Connection: keep-alive

{
        "product_id": "any-perk-id"
}
----------------------------------------------------------------
HTTP/1.1 401 Unauthorized
Content-Length: 54
Content-Security-Policy: default-src https:
Date: Tue, 24 Mar 2020 10:17:20 GMT
Referrer-Policy: no-referrer
Strict-Transport-Security: max-age=315360000; includeSubdomains; preload
Www-Authenticate: Bearer realm="fp",error="invalid_token",error_description="token expired"
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-Xss-Protection: 1; mode=block
Content-Type: text/plain; charset=utf-8

{"code": "UNAUTHENTICATED", "message":"token expired"}
*******************************************************
'''


def test_parse_traces():
    # Enqueue the trace lines
    q = Queue()
    for line in trace.splitlines():
        q.put(line)

    # Process
    it = parser.parse_item(q)

    # Validate
    assert it.profile == '+447521168738'
    assert it.test_id == '01-01'
    assert it.test_name == 'Request User Profile'
    assert it.request == 'POST /product-management/v1/users/me/orders/unsubscribe HTTP/1.1\
Content-Type: application/json\
Authorization: Bearer eyJraWQiOiI0ZjI0MzM3NTI2NThmYTBjMTg4ZDM2MTdmNmNjNDY5ZjQ5NzJiOWYiLCJ0e\
XAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyMDAwMDAwMDAwMDAwMDE2NTQ0OCIsImF1dGhvcml6YXRpb25\
faWQiOiJjNGJlMmQ4NC1jM2M5LTRhZjQtOGI4Yi03YjM4Y2M0YThiYWQiLCJwdXJwb3NlIjoiaWRlbnRpZnktY3VzdG\
9tZXIgY3VzdG9tZXItc2VsZi1zZXJ2aWNlIiwiaXNzIjoiaHR0cHM6XC9cL2F1dGgudWstY2VydDAuYmFpa2FscGxhd\
GZvcm0uY29tXC8iLCJhdXRoZW50aWNhdGlvbl9jb250ZXh0IjpbeyJpZGVudGlmaWVyIjoidGVzdDkxOTY1MjA4QHN0\
Zi5yZWYubzIuY28udWsiLCJ0eXBlIjoiZW1haWwifV0sImFjdGl2ZSI6dHJ1ZSwiY2xpZW50X2lkIjoibm92dW0tbXl\
0ZWxjbyIsImlkZW50aWZpZXJfYm91bmRfc2NvcGUiOltdLCJhdWQiOiJodHRwczpcL1wvYXBpLnVrLWNlcnQwLmJhaW\
thbHBsYXRmb3JtLmNvbSIsInNjb3BlIjoib2ZmbGluZV9hY2Nlc3Mgb3BlbmlkIGV2ZW50LWxvdy1kYXRhLXJlYWQgd\
XNlcnByb2ZpbGUtcmVhZCBhdXJhaWQtcmVhZCBteW8ybWlkZGxld2FyZS1yZWFkIHdlYnZpZXdzLXBob25lLW51bWJl\
ci1yZWFkIGV2ZW50LXN1YnNjcmlwdGlvbi10eXBlLW1pZ3JhdGlvbi1yZWFkIGF1dGhlbnRpY2F0aW9uLWluZm9ybWF\
0aW9uLXJlYWQgZXZlbnQtbG93LXZvaWNlLXJlYWQgd2Vidmlld3MtdXNlci1yZWFkIHByb2R1Y3QtbWFuYWdlbWVudC\
1vcmRlcnMtdXNlci1yZWFkIGV2ZW50LWJhci1hbGVydC1yZWFkIGV2ZW50LW5vLWRhdGEtcmVhZCBleHBsb3JlLWNvb\
nRlbnQtY2FyZC1kZXRhaWxzLXBob25lLW51bWJlci1yZWFkIHN1YnNjcmliZWQtcHJvZHVjdHMtcmVhZCBtb2JpbGUt\
YmFsYW5jZS1yZWFkIGV2ZW50LW5vLWJhbGFuY2UtcmVhZCBzdWJzY3JpYmVkLXByb2R1Y3RzLXVzZXItcmVhZCBpbnZ\
vaWNpbmctcGhvbmUtbnVtYmVyLXJlYWQgZXZlbnQtYXBwb2ludG1lbnQtcmVtaW5kZXItcmVhZCBldmVudC1pbnZvaW\
NlLWRlYml0LXJlYWQgZXZlbnQtcGF5bWVudC1hbGVydC1yZWFkIG15bzJtaWRkbGV3YXJlLXdyaXRlIGF1cmFpZC13c\
ml0ZSBtb2JpbGUtcXVvdGEtcmVhZCBzdWJzY3JpYmVkLXByb2R1Y3RzLXBob25lLW51bWJlci1yZWFkIGV2ZW50LW5v\
LXZvaWNlLXJlYWQgbm90aWZpY2F0aW9ucy1yZWFkIGV2ZW50LWhpZ2gtc3BlbmQtYWxlcnQtcmVhZCB0aW1lbGluZS1\
yZWFkIHByb2R1Y3QtbWFuYWdlbWVudC1vcmRlcnMtdXNlci13cml0ZSBldmVudC1kaXNjb25uZWN0aW9uLWFsZXJ0LX\
JlYWQgZXZlbnQtaW52b2ljZS1wYXltZW50LWR1ZS1yZWFkIG1vYmlsZS1iYWxhbmNlLXRvcC11cC13cml0ZSBpbnZva\
WNpbmctdXNlci1yZWFkIGV2ZW50LWxvdy1iYWxhbmNlLXJlYWQgcHJvZHVjdC1tYW5hZ2VtZW50LW9yZGVycy1waG9u\
ZS1udW1iZXItd3JpdGUgZXhwbG9yZS1jb250ZW50LW1vZHVsZXMtdXNlci1yZWFkIGlzc3Vlcy1jcmVhdGUgZXhwbG9\
yZS1jb250ZW50LWNhcmQtZGV0YWlscy11c2VyLXJlYWQgbW9iaWxlLWJhbGFuY2UtdG9wLXVwLXJlYWQgaW52b2ljaW\
5nLXJlYWQgZXZlbnQtaW52b2ljZS1yZXRhaW5lZC1yZWFkIGV4cGxvcmUtY29udGVudC1tb2R1bGVzLXBob25lLW51b\
WJlci1yZWFkIHByb2R1Y3QtbWFuYWdlbWVudC1vcmRlcnMtcGhvbmUtbnVtYmVyLXJlYWQgaXNzdWVzLXJlYWQgZXZl\
bnQtaW52b2ljZS1jaGFyZ2UtcmVhZCIsImFjcl92YWx1ZXMiOiIzIiwiZXhwIjoxNTg0NzIyMzEyLCJpYXQiOjE1ODQ\
3MTg3MTIsImp0aSI6IjU0OWY5NGY5LWQwNGItNDAxNC05MzUyLTBhOGZhNTI3ODI1MSJ9.ULKQ3FnZ-8bONmiBkBKsK\
-4waxsmjU_ieegEaPNsA6jwJqYprC2qab0wEbaT1ZtqBA0KhLViZo0qhNFNZJdfWd0hTDcL3Q_2TJ953UcF0ylLnA1D\
fraZkiEw7LVBxdRoi4zUI9r_kiryczSEVxd0-6ZUWQeW38XaZ_x4hb9FtCy6RS06KrG1VYCpJN-kEyw054ptiNsIgym\
jpcfRjx9WPsS_TLbCQg-rBLDZX-Fy0Qh4J-1FzO61VHfIuzO6SZwAP0DlduPhxQ8xSBusYp9MR5jvhtmaFTQQZritKa\
q9wjdvw7IDFEDB_PuEeBsIAoXwKorP1G5TNbJhTf_pq07dfg\
User-Agent: PostmanRuntime/7.22.0\
Accept: */*\
Cache-Control: no-cache\
Postman-Token: e189ab0d-1905-4930-a5af-991feb575eda\
Host: api.uk-cert0.baikalplatform.com\
Accept-Encoding: gzip, deflate, br\
Content-Length: 34\
Connection: keep-alive\
{\
        "product_id": "any-perk-id"\
}'

    assert it.response == 'HTTP/1.1 401 Unauthorized\
Content-Length: 54\
Content-Security-Policy: default-src https:\
Date: Tue, 24 Mar 2020 10:17:20 GMT\
Referrer-Policy: no-referrer\
Strict-Transport-Security: max-age=315360000; includeSubdomains; preload\
Www-Authenticate: Bearer realm="fp",error="invalid_token",error_description="token expired"\
X-Content-Type-Options: nosniff\
X-Frame-Options: SAMEORIGIN\
X-Xss-Protection: 1; mode=block\
Content-Type: text/plain; charset=utf-8\
\
{"code": "UNAUTHENTICATED", "message":"token expired"}'
