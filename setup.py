from setuptools import setup
import os

req_file = open(os.path.join(os.getcwd(), 'requirements.txt'), 'r')
lines = req_file.readlines()
requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]

setup(
    name='pytest-cache',
    description='pytest plugin with mechanisms for caching across test runs',
    long_description=open("README.md").read(),
    version='1.0dev2',
    author='Holger Krekel',
    author_email='holger.krekel@gmail.com',
    maintainer='Long Ho',
    maintainer_email='holevietlong@gmail.com',
    url='https://github.com/longlho/pytest-cache.git',
    py_modules=['pytest_cache'],
    entry_points={'pytest11': ['cacheprovider = pytest_cache']},
    install_requires=requirements,
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Topic :: Software Development :: Testing',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3'],
)
