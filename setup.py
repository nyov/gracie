#! /usr/bin/python
# -*- coding: utf-8 -*-

# setup.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2007–2010 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-2’ for details.

""" Python distutils setup for ‘gracie’ distribution.
    """

import distutils.cmd
import distutils.command.build
import distutils.command.install
import distutils.command.clean
import distutils.log
import distutils.util
import os
import os.path
import glob
import errno
import subprocess
import re
import textwrap

from setuptools import setup, find_packages
import docutils.core


distribution_name = "gracie"
main_module_name = 'gracie'
main_module = __import__(main_module_name, fromlist=['version'])
version = main_module.version

main_module_doc = main_module.__doc__.decode('utf-8')
short_description, long_description = (
    textwrap.dedent(desc).strip()
    for desc in main_module_doc.split('\n\n', 1)
    )


def is_source_file_newer(source_path, destination_path, force=False):
    """ Return True if destination is older than source or does not exist. """
    if force:
        result = True
    else:
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
        ("force", 'f',
         "Forcibly build everything (ignore file timestamps)."),
        ("html-src-files=", None,
         "Source files to build to HTML documents."),
        ("manpage-8-src-files=", None,
         "Source files to build to Unix manpages for section 8."),
        ("logo-src-file=", None,
         "Source SVG document for project logo."),
        ]

    boolean_options = ['force']

    def initialize_options(self):
        """ Initialise command options to defaults. """
        self.document_transforms = {
            'html': {
                'func': render_rst_document,
                'source_name_option': 'html_src_files',
                'writer_name': 'html',
                'source_suffix_regex': re.compile("\.txt$"),
                'dest_suffix': ".html",
                },
            'manpage.8': {
                'func': render_rst_document,
                'source_name_option': 'manpage_8_src_files',
                'writer_name': 'manpage',
                'source_suffix_regex': re.compile("\.8\.txt$"),
                'dest_suffix': ".8",
                },
            'logo': {
                'func': render_svg_document,
                'source_name_option': 'logo_src_file',
                'size': 80,
                'format': 'PNG',
                'source_suffix_regex': re.compile("\.svg$"),
                'dest_suffix': ".png",
                },
            }

        self.force = None

        for transform in self.document_transforms.values():
            option_name = transform['source_name_option']
            setattr(self, option_name, None)

    def finalize_options(self):
        """ Finalise command options before execution. """
        self.set_undefined_options(
            'build',
            ('force', 'force'))

        for (transform_name, transform) in self.document_transforms.items():
            source_paths = []
            option_name = transform['source_name_option']
            source_files_option_value = getattr(self, option_name, None)
            if source_files_option_value is not None:
                source_paths = source_files_option_value.split()
            transform['source_paths'] = source_paths

    def _render_documents(self, transform):
        """ Render documents that are not up-to-date. """
        for in_file_path in transform['source_paths']:
            out_file_base = re.sub(
                transform['source_suffix_regex'], "",
                in_file_path)
            out_file_path = out_file_base + transform['dest_suffix']
            render_document_func = transform['func']
            if is_source_file_newer(in_file_path, out_file_path, self.force):
                out_file_dir = os.path.dirname(out_file_path)
                if not os.path.isdir(out_file_dir):
                    self.mkpath(out_file_dir)
                render_document_func(in_file_path, out_file_path, transform)

    def run(self):
        """ Execute this command. """
        for transform in self.document_transforms.values():
            self._render_documents(transform)


class BuildCommand(distutils.command.build.build):
    """ Custom ‘build’ command for this distribution. """

    sub_commands = (
        [('build_doc', lambda self: True)]
        + distutils.command.build.build.sub_commands)


class InstallCommand(distutils.command.install.install):
    """ Custom ‘install’ command for this distribution. """

    sub_commands = (
        [('build_doc', lambda self: True)]
        + distutils.command.install.install.sub_commands)


def render_rst_document(in_file_path, out_file_path, transform):
    """ Render a document from source to dest using specified writer. """
    in_file_path = distutils.util.convert_path(in_file_path)
    out_file_path = distutils.util.convert_path(out_file_path)
    writer = transform['writer_name']
    distutils.log.info(
        "using writer %(writer)r to render document"
        " %(in_file_path)r -> %(out_file_path)r"
        % vars())
    docutils.core.publish_file(
        source_path=in_file_path,
        destination_path=out_file_path,
        writer_name=transform['writer_name'])


def render_svg_document(in_file_path, out_file_path, transform):
    """ Render SVG document to destination logo file. """
    in_file_path = distutils.util.convert_path(in_file_path)
    out_file_path = distutils.util.convert_path(out_file_path)
    geometry = "%(size)dx%(size)d" % transform
    render_process_args = [
        "gm", "convert",
        "-format", "SVG", in_file_path,
        "-geometry", geometry,
        "-format", transform['format'], out_file_path,
        ]
    distutils.log.info(
        "rendering logo %(in_file_path)r -> %(out_file_path)r"
        % vars())
    subprocess.call(render_process_args)


class CleanDocumentationCommand(distutils.cmd.Command):
    """ Clean files generated for this distribution's documentation. """
    user_options = [
        ("all", 'a',
         "Remove all build output, not just temporary by-products."),
        ("generated-files=", None,
         "File globs of generated documentation files."),
        ]

    boolean_options = ['all']

    def initialize_options(self):
        """ Initialise command options to defaults. """
        self.all = None

        self.generated_files = None

    def finalize_options(self):
        """ Finalise command options before execution. """
        self.set_undefined_options(
            'clean',
            ('all', 'all'))

        if self.generated_files:
            self.generated_file_globs = self.generated_files.split()
        else:
            self.generated_file_globs = []

    def run(self):
        """ Execute this command. """
        generated_file_paths = set()
        for file_glob in self.generated_file_globs:
            generated_file_paths.update(set(
                glob.glob(file_glob)))
        for file_path in generated_file_paths:
            os.remove(file_path)


class CleanCommand(distutils.command.clean.clean, object):
    """ Custom ‘clean’ command for this distribution. """

    sub_commands = (
        [('clean_doc', lambda self: True)]
        + distutils.command.clean.clean.sub_commands)

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
        super(CleanCommand, self).run()


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
        "build": BuildCommand,
        "build_doc": BuildDocumentationCommand,
        "install": InstallCommand,
        "clean": CleanCommand,
        "clean_doc": CleanDocumentationCommand,
        },

    # Setuptools metadata.
    zip_safe=False,
    install_requires=[
        "setuptools",
        "docutils >=0.6",
        "python-daemon >=1.4.5",
        "python-openid >=1.2",
        "Routes >=1.6.3",
        ],
    tests_require=[
        "MiniMock >= 1.2.2",
        ],
    test_suite="test.suite",

    # PyPI metadata.
    author=version.author_name,
    author_email=version.author_email,
    description=short_description,
    keywords=[
        "gracie", "openid", "identity", "authentication", "provider",
        ],
    url=main_module._url,
    long_description=long_description,
    license=version.license,
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
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
