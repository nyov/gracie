# -*- coding: utf-8 -*-

# test/test_gracied.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for gracied daemon module.
    """

import sys
import os
from StringIO import StringIO
import daemon
from daemon import pidlockfile

import scaffold
from scaffold import Mock

module_name = 'gracied'
module_file_under_test = os.path.join(scaffold.bin_dir, module_name)
gracied = scaffold.make_module_from_file(
    module_name, module_file_under_test
    )


class Stub_GracieServer(object):
    """ Stub class for GracieServer """

    version = "3.14.test"

    def __init__(self, socket_params, opts):
        """ Set up a new instance """

    def serve_forever(self):
        pass


def setup_gracie_fixtures(testcase):
    """ Set up fixtures for Gracie test cases. """
    testcase.mock_tracker = scaffold.MockTracker()

    testcase.app_class = gracied.Gracie

    testcase.stdout_test = StringIO()
    scaffold.mock("sys.stdout", mock_obj=testcase.stdout_test)

    scaffold.mock(
        "gracied.OptionParser.error",
        raises=SystemExit,
        tracker=testcase.mock_tracker)

    scaffold.mock(
        "gracied.GracieServer",
        returns=Mock(
            "gracied.GracieServer",
            tracker=testcase.mock_tracker),
        tracker=testcase.mock_tracker)

    scaffold.mock("gracied.default_port", mock_obj=7654)

    testcase.valid_apps = {
        'simple': dict(
            ),
        'argv_loglevel_debug': dict(
            options = ["--log-level", "debug"],
            ),
        'change-host': dict(
            options = ["--host", "frobnitz"],
            host = "frobnitz",
            ),
        'change-port': dict(
            options = ["--port", "9779"],
            port = 9779,
            ),
        'change-address': dict(
            options = ["--host", "frobnitz", "--port", "9779"],
            host = "frobnitz",
            port = 9779,
            ),
        'change-root-url': dict(
            options = ["--root-url", "http://spudnik/spam"],
            root_url = "http://spudnik/spam",
            ),
        'change-address-and-root-url': dict(
            options = [
                "--host", "frobnitz", "--port", "9779",
                "--root-url", "http://spudnik/spam",
                ],
            host = "frobnitz",
            port = 9779,
            root_url = "http://frobnitz/spam",
            ),
        }

    for key, params in testcase.valid_apps.items():
        argv = ["progname"]
        options = params.get('options', None)
        if options:
            argv.extend(options)
        params['argv'] = argv
        args = dict(
            argv=argv
            )
        params['args'] = args
        instance = testcase.app_class(**args)
        params['instance'] = instance


class Gracie_TestCase(scaffold.TestCase):
    """ Test cases for Gracie class. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_gracie_fixtures(self)

        scaffold.mock(
            "gracied.Gracie._become_daemon",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_instantiate(self):
        """ New Gracie instance should be created """
        for params in self.valid_apps.values():
            instance = params['instance']
            self.failIfIs(instance, None)

    def test_init_configures_logging(self):
        """ Gracie instance should configure logging """
        params = self.valid_apps['simple']
        args = params['args']
        logging_prev = gracied.logging
        scaffold.mock(
            "gracied.logging",
            tracker=self.mock_tracker)
        expect_mock_output = """\
           Called gracied.logging.basicConfig(...)
           """
        instance = self.app_class(**args)
        gracied.logging = logging_prev
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_wrong_arguments_invokes_parser_error(self):
        """ Wrong number of cmdline arguments should invoke parser error """
        invalid_argv_params = [
            ["progname", "foo",]
            ]
        expect_error = gracied.OptionParser.error.mock_raises
        expect_mock_output = """\
            Called gracied.OptionParser.error("...")
            """
        for argv in invalid_argv_params:
            args = dict(argv=argv)
            try:
                instance = self.app_class(**args)
            except expect_error:
                pass
            self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_opts_version_performs_version_action(self):
        """ Gracie instance should perform version action """
        argv = ["progname", "--version"]
        args = dict(argv=argv)
        scaffold.mock(
            "gracied.version", tracker=self.mock_tracker)
        version_test = "Foo.Boo"
        gracied.version.version_full = version_test
        expect_stdout = """\
            ...%(version_test)s...
            """ % vars()
        self.failUnlessRaises(
            SystemExit,
            self.app_class, **args
            )
        self.failUnlessOutputCheckerMatch(
            expect_stdout, self.stdout_test.getvalue()
            )

    def test_opts_help_performs_help_action(self):
        """ Gracie instance should perform help action """
        argv = ["progname", "--help"]
        args = dict(argv=argv)
        expect_stdout = """\
            Usage: ...
            """
        self.failUnlessRaises(
            SystemExit,
            self.app_class, **args
            )
        self.failUnlessOutputCheckerMatch(
            expect_stdout, self.stdout_test.getvalue()
            )

    def test_opts_loglevel_accepts_specified_value(self):
        """ Gracie instance should accept log-level setting """
        want_loglevel = "DEBUG"
        argv = ["progname", "--log-level", want_loglevel]
        args = dict(argv=argv)
        instance = self.app_class(**args)
        self.failUnlessEqual(want_loglevel, instance.opts.loglevel)

    def test_opts_datadir_accepts_specified_value(self):
        """ Gracie instance should accept data-dir setting """
        want_dir = "/foo/bar"
        argv = ["progname", "--data-dir", want_dir]
        args = dict(argv=argv)
        instance = self.app_class(**args)
        self.failUnlessEqual(want_dir, instance.opts.datadir)

    def test_opts_host_accepts_specified_value(self):
        """ Gracie instance should accept host setting """
        want_host = "frobnitz"
        argv = ["progname", "--host", want_host]
        args = dict(argv=argv)
        instance = self.app_class(**args)
        self.failUnlessEqual(want_host, instance.opts.host)

    def test_opts_port_accepts_specified_value(self):
        """ Gracie instance should accept port setting """
        want_port = 9779
        argv = ["progname", "--port", str(want_port)]
        args = dict(argv=argv)
        instance = self.app_class(**args)
        self.failUnlessEqual(want_port, instance.opts.port)

    def test_opts_root_url_accepts_specified_value(self):
        """ Gracie instance should accept root_url setting """
        want_url = "http://spudnik/spam"
        argv = ["progname", "--root-url", want_url]
        args = dict(argv=argv)
        instance = self.app_class(**args)
        self.failUnlessEqual(want_url, instance.opts.root_url)


class Gracie_main_TestCase(scaffold.TestCase):
    """ Test cases for Gracie.main method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_gracie_fixtures(self)

        scaffold.mock(
            "gracied.Gracie._become_daemon",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_instantiates_server(self):
        """ Should create a new server instance. """
        params = self.valid_apps['simple']
        instance = params['instance']
        host = gracied.default_host
        port = gracied.default_port
        expect_mock_output = """\
            Called gracied.GracieServer(
                (%(host)r, %(port)r),
                <Values at ...: {...}>)
            ...""" % vars()
        instance.main()
        self.failUnlessMockCheckerMatch(expect_mock_output)
        self.failIfIs(instance.server, None)

    def test_sets_specified_socket_params(self):
        """ Should set the server on the specified host:port. """
        for params in self.valid_apps.values():
            instance = params['instance']
            default_address = (
                gracied.default_host, gracied.default_port
                )
            host = params.get('host', gracied.default_host)
            port = params.get('port', gracied.default_port)
            if (host, port) == default_address:
                continue
            expect_mock_output = """\
                Called gracied.GracieServer(
                    (%(host)r, %(port)r),
                    <Values at ...: {...}>)
                ...""" % vars()
            instance.main()
            self.failUnlessMockCheckerMatch(expect_mock_output)
            self.mock_tracker.clear()

    def test_becomes_daemon(self):
        """ Should attempt to become a daemon. """
        params = self.valid_apps['simple']
        instance = params['instance']
        expect_mock_output = """\
            ...
            Called gracied.Gracie._become_daemon()
            ...
            """
        instance.main()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_starts_server(self):
        """ Should start GracieServer if child fork. """
        params = self.valid_apps['simple']
        instance = params['instance']
        port = gracied.default_port
        expect_mock_output = """\
            ...
            Called gracied.GracieServer.serve_forever()
            """
        instance.main()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class Gracie_become_daemon_TestCase(scaffold.TestCase):
    """ Test cases for Gracie._become_daemon method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_gracie_fixtures(self)

        self.mock_context = scaffold.Mock(
            "DaemonContext",
            tracker=self.mock_tracker)

        # Ensure that using this object as a context manager will call
        # the appropriate method.
        self.mock_context.__enter__.mock_returns_func = (
            self.mock_context.open)

        scaffold.mock(
            "daemon.DaemonContext",
            returns=self.mock_context,
            tracker=self.mock_tracker)

        self.test_pidfile_name = "BoGuS_NaMe"
        scaffold.mock(
            "gracied.pidfile_name",
            mock_obj=self.test_pidfile_name,
            tracker=self.mock_tracker)

        self.test_working_directory = "BoGuS_DiR"
        scaffold.mock(
            "os.getcwd",
            returns=self.test_working_directory,
            tracker=self.mock_tracker)

        self.mock_lockfile = scaffold.Mock(
            "PIDLockFile",
            tracker=self.mock_tracker)

        scaffold.mock(
            "pidlockfile.PIDLockFile",
            returns=self.mock_lockfile,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_creates_pidlockfile(self):
        """ Should create a PIDLockFile. """
        params = self.valid_apps['simple']
        instance = params['instance']
        pidfile_path = os.path.join(
            self.test_working_directory, self.test_pidfile_name)
        expect_mock_output = """\
            ...
            Called pidlockfile.PIDLockFile(%(pidfile_path)r)
            ...""" % vars()
        instance._become_daemon()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_creates_daemon_context(self):
        """ Should create a DaemonContext instance with expected args. """
        params = self.valid_apps['simple']
        instance = params['instance']
        expect_pidfile = self.mock_lockfile
        expect_files_preserve = [
            sys.stderr,
            ]
        expect_mock_output = """\
            ...
            Called daemon.DaemonContext(
                files_preserve=%(expect_files_preserve)r,
                pidfile=%(expect_pidfile)r)
            ...""" % vars()
        instance._become_daemon()
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_invokes_daemon_context_open(self):
        """ Should invoke DaemonContext open method. """
        params = self.valid_apps['simple']
        instance = params['instance']
        expect_mock_output = """\
            ...
            Called DaemonContext.open()
            """
        instance._become_daemon()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_stores_daemon_context(self):
        """ Should store daemon context as attribute of app. """
        params = self.valid_apps['simple']
        instance = params['instance']
        expect_context = self.mock_context
        instance._become_daemon()
        self.failUnlessIs(expect_context, instance.daemon_context)


class ProgramMain_TestCase(scaffold.ProgramMain_TestCase):
    """ Test cases for program __main__ function. """

    def setUp(self):
        """ Set up test fixtures """
        self.program_module = gracied
        self.application_class = gracied.Gracie
        super(ProgramMain_TestCase, self).setUp()
