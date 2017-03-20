# RETS Changelog

## 0.2.0
* Significatn changes to exception raising. No more InvalidFormat exception. ValueErrors are more appropriate for
input errors and RETSExceptions for consistently handling non-zero reply codes from the RETS Server. The RETSException
now has reply_code and reply_text parameters. 

## 0.1.3
* get_object requests with location=1 now parse the response appropriately

## 0.1.2
* getObject dictionaries now include md5 fingerprints as content_md5

## 0.1.1
* Multipart image downloads working in Python2. Still not working in Python3

## 0.1.0
* No results continues generator

## 0.0.12
* Action capability called correctly
* RETS Version no longer strips RETS/ prematurely
* Added additional INVALID_VERSION reply code for cathing STANDARD_XML
* Minor Bug Fixes

## 0.0.8 
* Removing lxml from requirements
* Parsing STANDARD-XML
* Removing need to manage RETS version
* User Agent Auth

## 0.0.7
* Streaming search results
