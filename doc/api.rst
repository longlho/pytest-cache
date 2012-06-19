
.. api:

config.cache API 
========================================

The ``pytest-cache`` plugin adds a ``config.cache`` 
object during the configure-initialization of pytest.
This allows other plugins, including ``conftest.py`` files,
to safely and flexibly store and retrieve values across
test runs because the ``config`` object is available
in many places.

Under the hood, the cache plugin uses the simple
`dumps/loads`_ API of the cross-interpreter 
execnet_ communication library. It makes it safe
to store values e. g. under Python2 and retrieve
it later from a Python3 or PyPy interpreter.

.. _`dumps/loads`: http://codespeak.net/execnet/basics.html#dumps-loads
.. _`execnet`: http://codespeak.net/execnet/

.. currentmodule:: pytest_cache

.. automethod:: Cache.get
.. automethod:: Cache.set
.. automethod:: Cache.makedir

