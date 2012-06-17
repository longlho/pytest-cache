from setuptools import setup
setup(
    name='pytest-cache',
    description='pytest plugin with mechanisms for caching across test runs',
    long_description=open("README.txt").read(),
    version='0.9',
    author='Holger Krekel',
    author_email='holger.krekel@gmail.com',
    url='http://bitbucket.org/hpk42/pytest-cache/',
    py_modules=['pytest_cache'],
    entry_points={'pytest11': ['cacheprovider = pytest_cache']},
    install_requires=['pytest>=2.2', 'execnet', ],
)
