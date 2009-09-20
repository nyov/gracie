#! /usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Package setup script.
    """

import textwrap

from setuptools import setup, find_packages

distribution_name = "gracie"
main_module_name = 'gracie'
main_module = __import__(main_module_name, fromlist=['version'])
version = main_module.version

short_description, long_description = (
    textwrap.dedent(desc).strip()
    for desc in main_module.__doc__.split('\n\n', 1)
    )


setup(
    name=distribution_name,
    version=version.version,
    packages=find_packages(
        exclude=['test'],
        ),
    scripts=[
        "bin/gracied",
        ],

    # setuptools metadata
    zip_safe=False,
    test_suite="test.suite",
    install_requires=[
        "setuptools",
        "python-daemon >= 1.4.5",
        "python-openid >= 1.2",
        "Routes >= 1.6.3",
        ],
    tests_require=[
        "MiniMock >= 1.2.2",
        ],

    # PyPI metadata
    author=version.author_name,
    author_email=version.author_email,
    description=short_description,
    license=version.license,
    keywords=[
        "gracie", "openid", "identity", "authentication", "provider",
        ],
    url=main_module._url,
    long_description=long_description,
    classifiers=[
        # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: System",
        "Operating System :: POSIX",
        "Intended Audience :: System Administrators",
        ],
    )


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
