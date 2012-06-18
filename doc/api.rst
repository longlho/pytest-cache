
.. api:

config.cache API 
========================================

The ``pytest-cache`` plugin adds a ``config.cache`` 
object during the configure-initialization of pytest.
The pytest config object is available in many places
which allows use to use caching functionality flexibly.

.. currentmodule:: pytest_cache

.. automethod:: Cache.get
.. automethod:: Cache.set
.. automethod:: Cache.getpath

