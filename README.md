[![PyPI version](https://badge.fury.io/py/rets.svg)](https://pypi.python.org/pypi/rets/)
[![Build Status](https://travis-ci.org/refindlyllc/rets.svg?branch=master)](https://travis-ci.org/refindlyllc/rets)
[![Coverage Status](https://coveralls.io/repos/github/refindlyllc/rets/badge.svg?branch=master)](https://coveralls.io/github/refindlyllc/rets?branch=master)


RETS
====

A pure python RETS client for real estate data.  Make requests to the MLS 
server to get real estate listings, media, and metadata.


# <a name="installation"></a>Installation
The easiest way to install is through pip.
`pip install rets`

If you need to build the package locally, it can be downloaded 
from [github](https://github.com/refindlyllc/rets) and installed 
through setuptools.

```
git clone https://github.com/refindlyllc/rets.git
cd python-rets
python setup.py install
```

You can now import the rets module within Python.

# Quickstart
After [installing](#installation) the rets package locally, 
make requests to an MLS server for data.

```
>>> from rets import Session
>>> login_url = 'http://retrsprovider.com/login'
>>> username = 'user123'
>>> password = 'a48a*32fa$5'
>>> rets_client = Session(login_url, username, password)
>>> rets_client.login()
>>> system_data = rets_client.get_system_metadata()
>>> system_data
{'version': '1.11.76004', 'system_description': 'MLS-RETS', 'system_id': 'MLS-RETS'}
>>> resources = rets_client.get_resource_metadata((resource='Agent')
>>> resources
{'ClassCount': '1',
 'ClassDate': '2016-04-20T15:17:13Z',
 'ClassVersion': '1.00.00023',
 'Date': '2016-12-08T16:15:15Z',
 'Description': 'Agent',
 'EditMaskDate': '2013-03-26T00:10:01Z',
 'EditMaskVersion': '1.00.00000',
 'KeyField': 'unique_id',
 'LookupDate': '2016-05-06T17:05:40Z',
 'LookupVersion': '1.00.00369',
 'ObjectDate': '2014-06-20T14:15:57Z',
 'ObjectVersion': '1.00.00001',
 'ResourceID': 'Agent',
 'SearchHelpDate': '2013-03-26T00:10:01Z',
 'SearchHelpVersion': '1.00.00000',
 'StandardName': 'Agent',
 'TableName': 'AGENT',
 'UpdateHelpDate': '2013-03-26T00:10:01Z',
 'UpdateHelpVersion': '1.00.00000',
 'ValidationExpressionDate': '2013-03-26T00:10:01Z',
 'ValidationExpressionVersion': '1.00.00000',
 'ValidationExternalDate': '2013-03-26T00:10:01Z',
 'ValidationExternalVersion': '1.00.00000',
 'ValidationLookupDate': '2013-03-26T00:10:01Z',
 'ValidationLookupVersion': '1.00.00000',
 'Version': '1.11.73255',
 'VisibleName': 'Agent'}
 
>>> search_results = rets_client.search(resource='Property', resource_class='RES', limit=1, dmql_query='(ListPrice=150000+)')
>>> for result in search_results:
...     result
 
 {'Acres': '0.0000',
  'ActiveOpenHouseCount': '',
  'AdditionalRooms': 'LAINRE,SCPOLA',
  'AmenRecFreq': '',
  'Amenities': 'BASKET,CLUBHO,COMPOO,COMSPA,EXEROO,EXTSTO,PRIMEM,PUTGRE,SAUNA,SIDEWA,STREET,TENCOU,UNDUTI',
  'AmenityRecFee': '0.00',
  'ApplicationFee': '100.00',
  'ApproxLivingArea': '1946',
  'AssociationMngmtPhone': '',
  'BathsFull': '2',
  'BathsHalf': '0',
  'BathsTotal': '2.00',
  'BedroomDesc': '',
  'Bedrooms': '3',
  'BedsTotal': '3',
  ...
   }
>>> rets_client.logout()
```


# The Session Object
All requests to a RETS server must be authenticated. The login credential
fields must be passed to the Session object at instantiation. As some
RETS servers limit the number of concurrent requests, it is also ideal
to logout when requests to the RETS server are complete. 

## Session Parameters 
- login_url: The login URL for the RETS feed
- username: The username for the RETS feed
- password: The password for the RETS feed
- version: The RETS version is typically provided from the server at login. 
You can set the version here to override the value provided by the server
- user_agent: The useragent for the RETS feed. Not all servers require this.
- user_agent_password: The useragent password for the RETS feed. Not all servers require this.
- follow_redirects: Follow HTTP redirects. The default True.
- use_post_method: Use HTTP POST method when making requests instead of GET. The default is True
- metadata_format: COMPACT_DECODED or STANDARD_XML. The client will attempt to set this automatically based on response codes from the RETS server.

## Context Manager
If you don't want to manually call the session's login and logout methods, 
the Session object can be opened in a context manager that logs the client
in and out automatically.

```
with Session(rets_client = Session(login_url, username, password) as s:
    print('Now logged in')
    system_metadata = s.get_system_metadata()
    search_results = s.search(resource='Property', resource_class='RES', limit=100, dmql_query='(ListPrice=150000+)')
print('Now logged out')
# do stuff with the search results
```

## Metadata Methods
The session object can get RETS metadata through the following methods:

### rets_client.get_system_metadata()
Returns the METADATA-SYSTEM information in a dictionary.

### rets_client.get_resource_metadata(resource=None)
Returns the METADATA-RESOURCE information in a list of dicts. The 
resource argument can be supplied to this method to limit the returned 
value to just the dict containing that resource.

### rets_client.get_class_metadata(resource)
Returns the METADATA-CLASS information for a given resource in a list
of dicts.

### rets_client.get_table_metadata(resource, class)
Returns the METADATA-TABLE information for a resource and class 
in a list of dicts.

### rets_client.get_object_metadata(resource)
Returns the METADATA-OBJECT information for a resource in a list of dicts

### rets_client.get_lookup_values(resource, lookup_name)
Returns the METADATA-LOOKUP_TYPE information for a field of a resource

## Object Methods
The session can get RETS Objects through the GetObject request. There 
are two methods for obtaining objects. 

### rets_client.get_preferred_object(resource, object_type, content_id, location=0)
Returns a dict containing information on the preferred object for a 
given content_id.

### rets_client.get_object(resource, object_type, content_ids, object_ids='*', location=0)
Returns a list of dicts containing information on objects for one or more
content_ids. The content_ids can be passed as a list if there are multiple
content_ids. The object_ids variable limits the objects returned to the index
number of each object on the server. This can be useful when getting a single
object or subset of total objects. Each dict contains a key of content_md5 that
contains the md5 checksum for the object. This should help users identify duplicates
supplied by the RETS servers or compare the objects against their previously
saved objects.

# Searching
Use the client's search method to search for real estate data. All searches
 must have the resource, class, and search query. The query can be sent 
 as either a Data Mining Query Language string or a search filter dictionary.
 
 The search method takes the following parameters:
 - resource: The resource that contains the class to search
 - resource_class: The class to search
 - search_filter=None: The query as a dict 
 - dmql_query=None: The query in dmql format
 - limit=None: Limit search values count
 - offset=None: Offset for RETS request. Useful when RETS limits number of results or transactions
 - optional_parameters=None: Values for option paramters
 
The resource and resource_class parameters are required. You must also provide either
the search_filter parameter or the dmql_query parameter.


The dmql query is what RETS is expecting and the search_filter dict ends up 
creating the dmql to be sent to rets.
```
>>> search_res = rets_client.search('Property', 'RES', dmql_query='(Status=A)')
>>> the_same_res = rets_client.search('Property', 'RES', search_filter={'Status': 'A"})
```

Many RETS servers limit the number of results returned with a search request. 
You may pass the limit and/or offset parameters to the search method to better
control the result set.

``` 
>>> small_res = rets_client.search('Property', 'RES', search_filter={'Status': 'A"}, limit=1)
```

The small_res just has a single listing returned.

```
>>> first_res = rets_client.search('Property', 'RES', search_filter={'Status': 'A"})
```

The RETS server only returned the first 10,000 results from this query. 
 Do a second query to get the rest of the results.
```
>>> second_res = rets_client.search('Property', 'RES', search_filter={'Status': 'A"}, offset=10000)
```

Lastly, if there are any other parameters to send to the Search end point,
 you may provide them in the optional_parameters dict.

## Filters
Complex queries in DQML can be troublesome to read and maintain. Creating
these queries as search_filter dictionaries can make this a little better.

The following logical operators are parsed by client.

 - $gte: numeric or datetime values greater than or equal to this.
 - $lte: numeric or datetime values less than or equal than to this.
 - $contains: a string contains these characters anywhere.
 - $begins: a string begins with these characters.
 - $ends: a string ends with these characters.
 - $in: a list of possible values a field can contain. 
 - $nin: a list of values a field cannot contain.
 - $neq: the value must not equal this.

Additionally, all date, datetime, and time objects passed to the search_filter
 are converted to the appropriate format expected by RETS server.

### Examples Search Filters
Active listings in the past 48 hours.
```
>>> two_days_ago = datetime.today() - datetime.timedelta(days=2)
>>> filter = {
        "Status": "Active",
        "CreatedDatetime": {
            "$gte": two_days_ago
            }
        }
>>> results = rets_client.search('Property', 'RES', search_filter=filter)
```

Expensive properties that have been on the market over 5 months
```
>>> five_months_ago = datetime.today() - datetime.timedelta(months=5)
>>> filter = {
        "Status": "Active",
        "CreatedDatetime": {
            "$lte": five_months_ago
            }
        }
    }
>>> results = rets_client.search('Property', 'RES', search_filter=filter)
```

Listings on a "Main" street in a neighborhood that contains "Quail West". 
(Some RETS use legal descriptions of neighborhood data or allow brokers to 
enter inconsistent neighborhood names)

```
>>> filter = {
        "Status": "Active",
        "StreetName": {
            "$begins": "Main S"
        },
        "DevelopmentName": {
            "$contains": "Quail West"
        }
>>> results = rets_client.search('Property', 'RES', search_filter=filter)
```

At least four bedrooms, two to three bathrooms, under $150,000.
```
>>> filter = {
        "Status": "Active",
        "Bedrooms": {
            "$gte": 4
        },
        "Bathrooms": {
            "$in": [2, 3]
        },
        "ListPrice": {
            "$lte": 150000
        }
    }
>>> results = rets_client.search('Property', 'RES', search_filter=filter)
```

## Search Results 
Searches with the RETS client return a list of dictionaries that represents listings of a search result.
 
## RETS Exceptions
There are many RETS Reply Codes that can be returned from the server. As a rule, this rets library raises a 
`rets.exceptions.RETSException` for all reply codes that are non-zero. The reply_code and reply_text are set as
parameters for the exception to make it easier for applications to catch and respond to specific reply codes. 

# Contributing
This RETS client has a long way to go, and keeping up with new [RESO Standards](http://www.reso.org/data-dictionary/)
, RETS 2.0, and other features will require ongoing maintenance. 
Please feel free to fork this repo and make pull requests to the development branch
 if you wish to contribute. Ensure that all new code has accompanying 
 tests. Travis-CI will run your code through the current and new tests 
 when you make a pull request.

All pull requests should reference an [Github issue](https://github.com/refindlyllc/rets/issues). Features 
and bugs should be discussed in the issue rather than be discussed in a pull request.

Many thanks to the passive contribution of [@troydavisson](https://github.com/troydavisson)
 for his work on [PHRETS](https://github.com/troydavisson/PHRETS). We shamelessly used many of his great conventions to
 make this project successful.

## Testing
If you wish to test the code prior to contribution use tox to test on python 2 and 3.
```bash
tox
```

## Helpful RETS Links
- http://www.reso.org/glossary/
- https://www.flexmls.com/developers/rets/tutorials/example-rets-session/
- http://www.realtor.org/retsorg.nsf/pages/docs
