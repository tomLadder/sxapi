#!/usr/bin/python
# coding: utf8

import os
import re

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)

# reqs is a list of requirement
reqs = [str(ir.req) for ir in install_reqs]

test_requirements = [
    "pytest", "mock"
]

with open('README.md') as readme_file:
    readme = readme_file.read()

# parse version
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'sxapi', "__init__.py")) as fdp:
    pattern = re.compile(r".*__version__ = '(.*?)'", re.S)
    VERSION = pattern.match(fdp.read()).group(1)

config = {
    'description': 'smaXtec API client',
    'author': 'Matthias Wutte',
    'long_description': readme,
    'url': '',
    'download_url': 'https://github.com/wuttem',
    'author_email': 'matthias.wutte@gmail.com',
    'version': VERSION,
    'install_requires': reqs,
    'tests_require': test_requirements,
    'packages': find_packages(),
    'scripts': [],
    'name': 'sxapi'
}

setup(**config)