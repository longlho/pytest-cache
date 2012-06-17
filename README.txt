pytest plugin providing caching of values and files between test runs.

Usage
---------

install via::

    easy_install pytest-cache # or
    pip install pytest-cache

after which other plugins can access a new `config.cache`_ object 
which helps sharing values between ``py.test`` invocations.

It also introduces a new option to rerun the last failing tests.


The new --lf (rerun last failing) option
------------------------------------------

The cache plugin introduces a new option to py.test which you 
can enable by default if you like to usually re-run the tests
that failed during the last run.  If no tests failed, passing 
``--lf`` has no effect and will trigger running of all tests.

Example::

    py.test --lf


.. _`config.cache`:

The new config.cache object
--------------------------------

Plugins or conftest.py support code can get a cached value 
using the pytest ``config`` object which is available in
many places::

    config.cache.get(key="myapp/somevalue", default=[1])

The key must be a ``/`` separated value. Usually the first
name is the name of your plugin or your application.  The
``somevalue`` part is a name that identifies a particular
value.  You must provide a default value which will be returned 
if no previous value was stored.  Values can be of any basic
python type, including nested types like e. g. lists of dictionaries.

You can set a new value for a cache entry like this::

    config.cache.set(key="myapp/somevalue", value=[1,2,3])

Note that when you store string values under a Python2 interpreter
they will be loaded as Python3 bytes.  If you store Python3
strings, they will be loaded as Python2 unicode objects.
IOW, if you are dealing with text make sure you use unicode 
on Python2 and things will be fine with your cache keys.
 

Notes
-------------

repository: http://bitbucket.org/hpk42/pytest-cache

Issues: repository: http://bitbucket.org/hpk42/pytest-cache/issues

more info on py.test: http://pytest.org


