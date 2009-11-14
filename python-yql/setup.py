
import os
import sys

from yql import __version__

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()

setup(name='yql',
    version=__version__,
    description='Python YQL - client library for YQL (Yahoo Query Language)',
    long_description=README,
    classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='web YQL',
    author="Stuart Colville",
    author_email="pypi@muffinresearch.co.uk",
    url="http://muffinresearch.co.uk/",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require = ['nosetests'],
    test_suite="yql.tests",
    entry_points = """\
    """
)

