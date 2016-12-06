[![Documentation Status](https://readthedocs.org/projects/python-rets/badge/?version=latest)](http://python-rets.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/rets.svg)](https://pypi.python.org/pypi/rets/)
[![Build Status](https://travis-ci.org/refindlyllc/python-rets.svg?branch=master)](https://travis-ci.org/refindlyllc/python-rets)
[![Coverage Status](https://coveralls.io/repos/github/refindlyllc/python-rets/badge.svg?branch=master)](https://coveralls.io/github/refindlyllc/python-rets?branch=master)

RETS
====

A python RETS client for real estate data.  Make requests to the MLS 
server to get real estate listings, media, and metadata.

[Documentation](http://python-rets.readthedocs.io/en/latest/)

###Warning
This package is not yet stable. 

### <a name="installation"></a>Installation
The easiest way to install is through pip.
`pip install rets`

If you need to build the package locally, it can be downloaded 
from [github](https://github.com/refindlyllc/python-rets) and installed 
through setuptools.

```
git clone https://github.com/refindlyllc/python-rets.git
cd python-rets
python setup.py install
```

You can now import the rets module within Python.

###Quickstart
After [installing](#installation) the rets package locally, we can
make requests to the MLS for data.

```
>>> import rets
>>> login_url = 'http://retrsprovider.com/login'
>>> username = 'user123'
>>> password = 'a48a*32fa$5'
>>> rets_version = '1.7.2'
>>> rets_client = rets.RETSClient(login_url,
                                  username,
                                  password,
                                  rets_version)
>>> rets_client
prettyprint of rets_client object
>>> rets_client.metadata
prettyprint of metadata
>>> resources = rets_client.get_resources()
>>> for r in resources:
...     print r
...     print r.get_classes()
 
prettyprint of classes and resources


# Get some homes over $400,000
>>> residential_class = res_client.get_resource('Property).get_class('RES')
>>> results_cursor = rets_client.search(class=residential_class,
                                        filter={'Status': 'A',
                                                'ListPrice': {'gte': 400000}}, 
                                        limit=10)

>>> for result in results_cursor:
...     print(result)

prettyprint some results
```


###Login
All requests to a RETS server must be authenticated. The login credential
fields can be passed to the RETSClient object at instantiation or set through
environment variables.

```
rets_client = rets.RETSClient(login_url='http://somelogin.url'
                              username='myusername',
                              password='changeme',
                              user-agent=NOne,
                              user-agent_password=None,
                              basic_auth=False
```

Not all RETS providers require all fields. If a user-agent, user-agent_password
 or basic authentication is not required, do not set those parameters.

###Searching

##Filters

###ResultsSet Cursor
Searches with the RETSClient return a results cursor. The cursor is an 
iterator that yields results as you loop through the iterator. This prevents
exceptionally large searches from consuming all of your memory by handling
each result discretely. 

##Metadata
discuss metadata 

##Media Objects
discuss media objects and how they are returned

##Using the Context Manager
with Session(asdf) as s:
do stuff
    
then it automatically disconnects from the server. Ths is important as most servers limit the number of 
concurrent connections.

###What about LibRets?
compare and contrast to librets. This is pure python, not c++.

###Contributing
This RETS client has a long way to go, and keeping up with new [RESO Standards](http://www.reso.org/data-dictionary/)
will require ongoing maintenance. Please feel free to fork this repo and make
pull requests to master if you wish to contribute. Please ensure that all new 
code has accompanying tests. Travis-CI will run your code through the current
and new tests when you make a pull request.

All pull requests should reference a [Github issue](https://github.com/refindlyllc/python-rets/issues). Features 
and bugs can be discussed in the features rather than be discussed in a pull request.

##Testing and Contribution
If you wish to test the code prior to contribution 
`nosetests --with-coverage --cover-package=rets`

##Helpful RETS Links
- http://www.reso.org/glossary/
- https://www.flexmls.com/developers/rets/tutorials/example-rets-session/
- http://www.realtor.org/retsorg.nsf/pages/docs
