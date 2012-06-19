import py
import pytest

__version__ = '0.9'

def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--lf', action='store_true', dest="lf",
        help="rerun tests that failed at the last run")
    group.addoption('--cache', action='store_true', dest="showcache",
        help="show cache contents, don't perform collection or tests")
    group.addoption('--rmcache', action='store_true', dest="rmcache",
        help="remove all cache contents at start of test run.")

def pytest_cmdline_main(config):
    if config.option.showcache:
        return showcache(config)

@pytest.mark.tryfirst
def pytest_configure(config):
    config.cache = cache = Cache(config)
    config.pluginmanager.register(LFPlugin(config), "lfplugin")

def pytest_report_header(config):
    relpath = py.path.local().bestrelpath(config.cache._cachedir)
    return "cache base dir: %s" % config.cache._cachedir

class Cache:
    def __init__(self, config):
        self.config = config
        self._cachedir = getrootdir(config, ".cache")
        self.trace = config.trace.root.get("cache")
        if config.getvalue("rmcache"):
            self.trace("clearing cachedir")
            self._cachedir.remove()
            self._cachedir.mkdir()

    def makedir(self, name):
        """ return a directory path object with the given name.  If the
        directory does not yet exist, it will be created.  You can use it
        to manage files likes e. g. store/retrieve database
        dumps across test sessions.

        :param name: must be a string not containing a ``/`` separator.
             Make sure the name contains your plugin or application
             identifiers to prevent clashes with other cache users.
        """
        if name.count("/") != 0:
            raise ValueError("name is not allowed to contain '/'")
        p = self._cachedir.join("d/" + name)
        p.ensure(dir=1)
        return p

    def _getpath(self, key):
        if not key.count("/") > 1:
            raise KeyError("Key must be of format 'dir/.../subname")
        return self._cachedir.join(key)

    def _getvaluepath(self, key):
        p = self._getpath("v/" + key)
        p.dirpath().ensure(dir=1)
        return p

    def get(self, key, default):
        """ return cached value for the given key.  If no value
        was yet cached or the value cannot be read, the specified
        default is returned.

        :param key: must be a ``/`` separated value. Usually the first
             name is the name of your plugin or your application.
        :param default: must be provided in case of a cache-miss or
             invalid cache values.

        """
        from execnet import loads, DataFormatError
        path = self._getvaluepath(key)
        if path.check():
            f = path.open("rb")
            try:
                try:
                    return loads(f.read())
                finally:
                    f.close()
            except DataFormatError:
                self.trace("cache-invalid at %s" % (key,))
        return default

    def set(self, key, value):
        """ save value for the given key.

        :param key: must be a ``/`` separated value. Usually the first
             name is the name of your plugin or your application.
        :param value: must be of any combination of basic
               python types, including nested types
               like e. g. lists of dictionaries.
        """
        from execnet import dumps, DataFormatError
        path = self._getvaluepath(key)
        f = path.open("wb")
        try:
            try:
                self.trace("cache-write %s: %r" % (key, value,))
                return f.write(dumps(value))
            finally:
                f.close()
        except DataFormatError:
            raise ValueError("cannot serialize a builtin python type")


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

def showcache(config):
    from _pytest.main import wrap_session
    return wrap_session(config, _showcache)

def _showcache(config, session):
    from pprint import pprint
    if not config.cache._cachedir.check():
        print("cache is empty")
        return 0
    tw = py.io.TerminalWriter()
    dummy = object()
    basedir = config.cache._cachedir
    vdir = basedir.join("v")
    tw.sep("-", "cache values")
    for valpath in vdir.visit(lambda x: x.check(file=1)):
        key = valpath.relto(vdir)
        val = config.cache.get(key, dummy)
        if val is dummy:
            tw.line("%s contains unreadable content, "
                  "will be ignored" % key)
        else:
            tw.line("%s contains:" % key)
            stream = py.io.TextIO()
            pprint(val, stream=stream)
            for line in stream.getvalue().splitlines():
                tw.line("  " + line)

    ddir = basedir.join("d")
    if ddir.check(dir=1) and ddir.listdir():
        tw.sep("-", "cache directories")
        for p in basedir.join("d").visit():
            #if p.check(dir=1):
            #    print("%s/" % p.relto(basedir))
            if p.check(file=1):
                key = p.relto(basedir)
                tw.line("%s is a file of length %d" % (
                        key, p.size()))


### XXX consider shifting part of the below to pytest config object

def getrootdir(config, name):
    """ return a best-effort root subdir for this test run.

    Starting from files specified at the command line (or cwd)
    search starts upward for the first "tox.ini", "pytest.ini",
    "setup.cfg" or "setup.py" file.  The first directory containing
    such a file will be used to return a named subdirectory
    (py.path.local object).

    """
    if config.inicfg:
        p = py.path.local(config.inicfg.config.path).dirpath()
    else:
        inibasenames = ["setup.py", "setup.cfg", "tox.ini", "pytest.ini"]
        for x in getroot(config.args, inibasenames):
            p = x.dirpath()
            break
        else:
            p = py.path.local()
            config.trace.get("warn")("no rootdir found, using %s" % p)
    subdir = p.join(name)
    config.trace("root %s: %s" % (name, subdir))
    return subdir

def getroot(args, inibasenames):
    args = [x for x in args if not str(x).startswith("-")]
    if not args:
        args = [py.path.local()]
    for arg in args:
        arg = py.path.local(arg)
        for base in arg.parts(reverse=True):
            for inibasename in inibasenames:
                p = base.join(inibasename)
                if p.check():
                    yield p
