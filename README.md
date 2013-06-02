pytest-cache: working with cross-testrun state
=====================================================

[![Build Status](https://secure.travis-ci.org/longlho/pytest-cache.png?branch=master)](http://travis-ci.org/longlho/pytest-cache)

Usage
---------

install via::

    pip install pytest-cache

after which other plugins can access a new `config.cache`_ object 
which helps sharing values between ``py.test`` invocations.

The plugin also introduces a new ``--lf`` option to rerun the 
last failing tests and a ``--clearcache`` option to remove 
cache contents ahead of a test run.


The new --lf (rerun last failing) option
------------------------------------------

The cache plugin introduces the ``--lf`` option to py.test which
alows to rerun all test failures of a previous test run.  
If no tests failed previously, all tests will be run as normal.  
It is thus usually fine to always pass ``--lf``.

As an example, let's create 50 test invocation of which
only 2 fail::

    # content of test_50.py
    import pytest

    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17,25):
           pytest.fail("bad luck") 

If you run this for the first time you will see two failures::

    $ py.test -q
    collecting ... collected 50 items
    .................F.......F........................
    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________
    
    i = 17
    
        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17,25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck
    
    test_50.py:6: Failed
    _______________________________ test_num[25] _______________________________
    
    i = 25
    
        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17,25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck
    
    test_50.py:6: Failed
    2 failed, 48 passed in 0.06 seconds

If you then run it with ``--lf`` you will re-run the last two failures::

    $ py.test -q --lf
    collecting ... collected 50 items
    FF
    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________
    
    i = 17
    
        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17,25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck
    
    test_50.py:6: Failed
    _______________________________ test_num[25] _______________________________
    
    i = 25
    
        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17,25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck
    
    test_50.py:6: Failed
    ======================== 48 tests deselected by '' =========================
    2 failed, 48 deselected in 0.01 seconds

The last line indicates that 48 tests have not been run.

.. _`config.cache`:

The new config.cache object
--------------------------------

.. regendoc:wipe

Plugins or conftest.py support code can get a cached value 
using the pytest ``config`` object.  Here is a basic example
plugin which implements a `funcarg <http://pytest.org/latest/funcargs.html>`_
which re-uses previously created state across py.test invocations::

    # content of test_caching.py
    import time

    def pytest_funcarg__mydata(request):
        val = request.config.cache.get("example/value", None)
        if val is None:
            time.sleep(9*0.6) # expensive computation :)
            val = 42
            request.config.cache.set("example/value", val)
        return val 

    def test_function(mydata):
        assert mydata == 23

If you run this command once, it will take a while because
of the sleep::

    $ py.test -q
    collecting ... collected 1 items
    F
    ================================= FAILURES =================================
    ______________________________ test_function _______________________________
    
    mydata = 42
    
        def test_function(mydata):
    >       assert mydata == 23
    E       assert 42 == 23
    
    test_caching.py:12: AssertionError
    1 failed in 5.43 seconds

If you run it a second time the value will be retrieved from
the cache and this will be quick::

    $ py.test -q
    collecting ... collected 1 items
    F
    ================================= FAILURES =================================
    ______________________________ test_function _______________________________
    
    mydata = 42
    
        def test_function(mydata):
    >       assert mydata == 23
    E       assert 42 == 23
    
    test_caching.py:12: AssertionError
    1 failed in 0.02 seconds

Consult the `pytest-cache API <http://packages.python.org/pytest-cache/api.html>`_
for more details.


Inspecting Cache content
-------------------------------

You can always peek at the content of the cache using the
``--cache`` command line option::

    $ py.test --cache
    =========================== test session starts ============================
    platform linux2 -- Python 2.7.3 -- pytest-2.2.5.dev2
    cachedir: /home/hpk/tmp/doc-exec-257/.cache
    ------------------------------- cache values -------------------------------
    cache/lastfailed contains:
      set(['test_caching.py::test_function'])
    example/value contains:
      42
    
    =============================  in 0.01 seconds =============================

Clearing Cache content
-------------------------------

You can instruct pytest to clear all cache files and values 
by adding the ``--clearcache`` option like this::

    py.test --clearcache

This is recommended for invocations from Continuous Integration
servers where isolation and correctness is more important
than speed.

Notes
-------------

more info on py.test: http://pytest.org


