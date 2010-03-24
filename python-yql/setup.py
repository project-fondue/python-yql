import os
import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, '../README')).read()
VERSION = 0.3

setup(name='yql',
    version=VERSION,
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
    install_requires = sys.version_info < (2,6) and ['httplib2', 'simplejson'] or ['httplib2'],
    tests_require = ['nosetests', 'coverage'],
    test_suite="tests",
    entry_points = """\
    """
)

