import pytest
import py
from textwrap import dedent

pytest_plugins = "pytester",

def test_version():
    import pytest_cache
    assert pytest_cache.__version__

def test_cache_reportheader(testdir):
    p = testdir.makepyfile("""
        def test_hello():
            pass
    """)
    cachedir = p.dirpath(".cache")
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "cache base dir: %s" % cachedir,
    ])

def test_cache_show(testdir):
    result = testdir.runpytest("--cache")
    assert result.ret == 0
    result.stdout.fnmatch_lines([
        "*cache is empty*"
    ])
    p = testdir.makeconftest("""
        def pytest_configure(config):
            config.cache.set("my/name", [1,2,3])
            config.cache.set("other/some", {1:2})
            config.cache.getpath("my/data.db").write("hello")
    """)
    result = testdir.runpytest()
    assert result.ret == 0
    result = testdir.runpytest("--cache")
    result.stdout.fnmatch_lines([
        "*cache base dir:*",
        "*my/data.db is a file of length*",
        "*my/name contains:",
        "  [1, 2, 3]",
        "*other/some contains*",
        "  {1: 2}",
    ])


class TestNewAPI:
    def test_config_cache_getpath(self, testdir):
        testdir.makeini("[pytest]")
        config = testdir.parseconfigure()
        pytest.raises(KeyError, lambda:
            config.cache.getpath("abc"))
        p = config.cache.getpath("key/name")
        assert not p.check()
        assert p.dirpath().check()

    def test_config_cache_dataerror(self, testdir):
        testdir.makeini("[pytest]")
        config = testdir.parseconfigure()
        p = config.cache.getpath("key/name")
        p.write("1p2o3i")
        val = config.cache.get("key/name", -2)
        assert val == -2

    def test_config_cache(self, testdir):
        testdir.makeconftest("""
            def pytest_configure(config):
                # see that we get cache information early on
                assert hasattr(config, "cache")
        """)
        testdir.makepyfile("""
            def test_session(pytestconfig):
                assert hasattr(pytestconfig, "cache")
        """)
        result = testdir.runpytest()
        assert result.ret == 0
        result.stdout.fnmatch_lines(["*1 passed*"])

    def XXX_test_cachefuncarg(self, testdir):
        testdir.makepyfile("""
            import pytest
            def test_cachefuncarg(cache):
                val = cache.get("some/thing", None)
                assert val is None
                cache.set("some/thing", [1])
                pytest.raises(TypeError, lambda: cache.get("some/thing"))
                val = cache.get("some/thing", [])
                assert val == [1]
        """)
        result = testdir.runpytest()
        assert result.ret == 0
        result.stdout.fnmatch_lines(["*1 passed*"])

class TestLastFailed:
    @pytest.mark.skipif("sys.version_info < (2,6)")
    def test_lastfailed_usecase(self, testdir, monkeypatch):
        monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", 1)
        p = testdir.makepyfile("""
            def test_1():
                assert 0
            def test_2():
                assert 0
            def test_3():
                assert 1
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*2 failed*",
        ])
        p.write(py.code.Source("""
            def test_1():
                assert 1

            def test_2():
                assert 1

            def test_3():
                assert 0
        """))
        result = testdir.runpytest("--lf")
        result.stdout.fnmatch_lines([
            "*2 passed*1 desel*",
        ])
        result = testdir.runpytest("--lf")
        result.stdout.fnmatch_lines([
            "*1 failed*2 passed*",
        ])
        result = testdir.runpytest("--lf", "--rmcache")
        result.stdout.fnmatch_lines([
            "*1 failed*2 passed*",
        ])
