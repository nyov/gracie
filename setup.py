#! /usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-2’ for details.

""" Package setup script.
    """

import distutils.cmd
import distutils.log
import os
import errno
import re
import textwrap

from setuptools import setup, find_packages
import docutils.core

distribution_name = "gracie"
main_module_name = 'gracie'
main_module = __import__(main_module_name, fromlist=['version'])
version = main_module.version

short_description, long_description = (
    textwrap.dedent(desc).strip()
    for desc in main_module.__doc__.split('\n\n', 1)
    )


def is_source_file_newer(source_path, destination_path):
    """ Return True if destination is older than source or does not exist. """
    source_stat = os.stat(source_path)
    source_ctime = source_stat.st_ctime
    try:
        destination_stat = os.stat(destination_path)
    except OSError, exc:
        if exc.errno == errno.ENOENT:
            destination_ctime = None
        else:
            raise
    else:
        destination_ctime = destination_stat.st_ctime
    result = (source_ctime > destination_ctime)
    return result


class BuildDocumentationCommand(distutils.cmd.Command):
    """ Build documentation for this distribution. """
    user_options = [
        ("html-src-files=", None,
         "Source files to build to HTML documents."),
        ("manpage-8-src-files=", None,
         "Source files to build to Unix manpages for section 8."),
        ]

    def initialize_options(self):
        """ Initialise command options to defaults. """
        self.document_transforms = {
            'html': {
                'writer_name': 'html',
                'source_suffix_regex': re.compile("\.txt$"),
                'dest_suffix': ".html",
                },
            'manpage.8': {
                'writer_name': 'manpage',
                'source_suffix_regex': re.compile("\.8\.txt$"),
                'dest_suffix': ".8",
                },
            }

        self.html_src_files = None
        self.manpage_1_src_files = None
        self.manpage_8_src_files = None

    def finalize_options(self):
        """ Finalise command options before execution. """
        for (transform_name, option_name) in [
            ('html', 'html_src_files'),
            ('manpage.8', 'manpage_8_src_files'),
            ]:
            transform = self.document_transforms[transform_name]
            source_paths = []
            source_files_option_value = getattr(self, option_name, None)
            if source_files_option_value is not None:
                source_paths = source_files_option_value.split()
            transform['source_paths'] = source_paths

    def _render_documents(self, transform):
        """ Render documents from reST source. """
        for in_file_path in transform['source_paths']:
            out_file_base = re.sub(
                transform['source_suffix_regex'], "",
                in_file_path)
            out_file_path = out_file_base + transform['dest_suffix']
            if is_source_file_newer(in_file_path, out_file_path):
                render_document(
                    in_file_path, out_file_path, transform['writer_name'])

    def run(self):
        """ Execute this command. """
        for transform in self.document_transforms.values():
            self._render_documents(transform)


def render_document(source_path, destination_path, writer_name):
    """ Render a document from source to destination. """
    distutils.log.info(
        "rendering document %(source_path)r -> %(destination_path)r"
        % vars())
    docutils.core.publish_file(
        source_path=source_path,
        destination_path=destination_path,
        writer_name=writer_name)


setup(
    name=distribution_name,
    version=version.version,
    packages=find_packages(
        exclude=['test'],
        ),
    scripts=[
        "bin/gracied",
        ],
    cmdclass={
        "build_doc": BuildDocumentationCommand,
        },

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
