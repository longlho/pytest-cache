import py
import pytest
from execnet.gateway_base import serialize, deserialize

__version__ = '0.9'


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--lf', action='store_true', dest="lf",
        help="rerun tests that failed at the last run")


@pytest.mark.tryfirst
def pytest_configure(config):
    config.cache = cache = Cache(config)
    config.pluginmanager.register(LFPlugin(config), "lfplugin")


class Cache:
    def __init__(self, config):
        self.config = config
        basepath = config.getinidir()
        if basepath is None:
            basepath = py.path.local()
        self._cachedir = basepath.ensure(".cache", dir=1)

    def getpath(self, key):
        """ get a filesystem path for the given key. There is no
        guarantee that the file exists. Missing intermediate
        directories will be created, however.
        """
        if not key.count("/") > 0:
            raise KeyError("Key must be of format 'dir/.../subname")
        p = self._cachedir.join(key)
        p.dirpath().ensure(dir=1)
        return p

    def get(self, key, default):
        path = self.getpath(key)
        if path.check():
            f = path.open("rb")
            try:
                return deserialize(f.read(), (False, False))
            finally:
                f.close()
        else:
            return default

    def set(self, key, value):
        path = self.getpath(key)
        f = path.open("wb")
        try:
            return f.write(serialize(value))
        finally:
            f.close()


class LFPlugin:
    """ Plugin which implements the --lf (run last-failing) option """
    def __init__(self, config):
        self.config = config
        if config.getvalue("lf"):
            self.lastfailed = self.config.cache.get("cache/lastfailed", set())

    def pytest_report_header(self):
        if self.config.getvalue("lf"):
            if not self.lastfailed:
                mode = "run all (no recorded failures)"
            else:
                mode = "rerun last %d failures" % len(self.lastfailed)
            return "run-last-failure: %s" % mode

    def pytest_collection_modifyitems(self, session, config, items):
        if self.config.getvalue("lf") and self.lastfailed:
            newitems = []
            deselected = []
            for item in items:
                if item.nodeid in self.lastfailed:
                    newitems.append(item)
                else:
                    deselected.append(item)
            items[:] = newitems
            config.hook.pytest_deselected(items=deselected)

    def pytest_sessionfinish(self):
        config = self.config
        terminal = config.pluginmanager.getplugin("terminalreporter")
        stats = terminal.stats
        failedreports = stats.get("failed", [])
        ids = set([x.nodeid for x in failedreports])
        config.cache.set("cache/lastfailed", ids)

