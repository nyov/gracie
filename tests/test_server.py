# -*- coding: utf-8 -*-

# tests/test_server.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for server module.
    """

import optparse

import scaffold

from gracie import server


def stub_server_bind(server):
    """ Stub method to get server location """
    (host, port) = server.server_address
    (server.server_name, server.server_port) = (host, port)

class Stub_HTTPServer(object):
    """ Stub class for HTTPServer """
    def __init__(
        self,
        server_address, RequestHandlerClass, gracie_server
        ):
        """ Set up a new instance """

    server_bind = stub_server_bind

class Stub_ResponseHeader(object):
    """ Stub class for response header """

    def __init__(self, code, protocol=None):
        self.code = code
        self.protocol = protocol
        self.fields = dict()

class Stub_Response(object):
    """ Stub class for Response """

    def __init__(self, header, data=None):
        """ Set up a new instance """
        self.header = header
        self.data = data


class Stub_ConsumerAuthStore(object):
    """ Stub class for ConsumerAuthStore """

    def __init__(self):
        self._authorisations = dict()

    def store_authorisation(self, auth_tuple, status):
        self._authorisations[auth_tuple] = status

    def is_authorised(self, auth_tuple):
        return self._authorisations.get(auth_tuple, False)

class Stub_ConsumerAuthStore_always_auth(Stub_ConsumerAuthStore):
    """ ConsumerAuthStore stub that always authorises """

    def is_authorised(self, auth_tuple):
        return True

class Stub_ConsumerAuthStore_never_auth(Stub_ConsumerAuthStore):
    """ ConsumerAuthStore stub that never authorises """

    def is_authorised(self, auth_tuple):
        return False


class Stub_SessionManager(object):
    """ Stub class for SessionManager """

    def store_session(self, session):
        pass

    def get_session(self, session_id):
        return None

    def remove_session(self, session_id):
        pass


class Stub_HTTPRequestHandler(object):
    """ Stub class for HTTPRequestHandler """


class Stub_OpenIDError(Exception):
    """ Stub error class for openid module """

class Stub_OpenIDStore(object):
    """ Stub class for openid backing store """

    def __init__(self, _, *args, **kwargs):
        """ Set up a new instance """

class Stub_OpenIDServer(object):
    """ Stub class for an OpenID protocol server """

    def __init__(self, store):
        """ Set up a new instance """

    def decodeRequest(self, request):
        return Stub_OpenIDResponse()

    def encodeResponse(self, response):
        return Stub_OpenIDWebResponse()

class Stub_OpenIDRequest(object):
    """ Stub class for an OpenID protocol request """

    def __init__(self, http_query, params=None):
        """ Set up a new instance """

        self.mode = http_query.get('openid.mode')
        keys = [
            'identity', 'trust_root', 'immediate', 'return_to',
            ]
        if params is None:
            params = dict()
        for key in keys:
            setattr(self, key, None)
            if key in params:
                setattr(self, key, params[key])

    def answer(self, allow, server_url=None):
        response = Stub_OpenIDResponse(dict(
            allow = allow,
            server_url = server_url,
            ))
        return response

class Stub_OpenIDResponse(object):
    """ Stub class for an OpenID protocol response """

    def __init__(self, params=None):
        self.params = params

    def encodeToURL(self):
        url = "http://stub/openid_response/" + ";".join(
            "%s=%s" % (key, val) for key, val in self.params.items()
            )
        return url

class Stub_OpenIDWebResponse(object):
    """ Stub class for an encoded OpenID response """

    def __init__(self):
        """ Set up a new instance """
        self.code = 200
        self.headers = {"openid": "yes"}
        self.body = "OpenID response"

def make_default_opts():
    """ Create commandline opts instance with required values """
    opts = optparse.Values(dict(
        datadir = "/tmp",
        host = "example.org", port = 9779,
        ))
    return opts


class GracieServer_TestCase(scaffold.TestCase):
    """ Test cases for GracieServer class. """

    def setUp(self):
        """ Set up test fixtures """
        self.mock_tracker = scaffold.MockTracker()

        self.server_class = server.GracieServer

        scaffold.mock(
            "server.OpenIDServer",
            mock_obj=Stub_OpenIDServer,
            tracker=self.mock_tracker)
        scaffold.mock(
            "server.OpenIDStore",
            mock_obj=Stub_OpenIDStore,
            tracker=self.mock_tracker)
        scaffold.mock(
            "server.ConsumerAuthStore",
            mock_obj=Stub_ConsumerAuthStore,
            tracker=self.mock_tracker)
        scaffold.mock(
            "server.SessionManager",
            mock_obj=Stub_SessionManager,
            tracker=self.mock_tracker)

        scaffold.mock(
            "server.HTTPServer",
            mock_obj=Stub_HTTPServer,
            tracker=self.mock_tracker)
        scaffold.mock(
            "server.HTTPRequestHandler",
            mock_obj=Stub_HTTPRequestHandler,
            tracker=self.mock_tracker)

        self.valid_servers = {
            'simple': dict(
                ),
            'with-opts': dict(
                opts = dict(
                    foo="spam",
                    bar="eggs",
                    ),
                ),
            'datadir': dict(
                opts = dict(
                    datadir = "/foo/bar",
                    ),
                datadir = "/foo/bar",
                ),
            }

        for key, params in self.valid_servers.items():
            args = params.get('args')
            if not args:
                args = dict()
            opts = make_default_opts()
            opts._update_loose(params.get('opts', dict()))
            params['opts'] = opts
            args.update(dict(
                socket_params=None,
                opts=opts,
                ))
            instance = self.server_class(**args)
            params['args'] = args
            params['instance'] = instance

    def tearDown(self):
        """ Tear down test fixtures """
        scaffold.mock_restore()

    def test_instantiate(self):
        """ New GracieServer instance should be created """
        for params in self.valid_servers.values():
            instance = params['instance']
            self.failIfIs(None, instance)

    def test_version_as_specified(self):
        """ GracieServer should have specified version string """
        params = self.valid_servers['simple']
        scaffold.mock(
            "server.version", tracker=self.mock_tracker)
        version_test = "1.414.test"
        server.version.version_full = version_test
        instance = self.server_class(**params['args'])
        self.failUnlessEqual(version_test, instance.version)

    def test_opts_as_specified(self):
        """ GracieServer should have specified opts mapping """
        params = self.valid_servers['with-opts']
        instance = params['instance']
        opts = params['opts']
        self.failUnlessEqual(opts, instance.opts)

    def test_server_creates_http_server(self):
        """ GracieServer should create an HTTP server """
        params = self.valid_servers['simple']
        args = params['args']
        opts = params['opts']
        server_address = (opts.host, opts.port)
        scaffold.mock(
            "server.HTTPServer", tracker=self.mock_tracker)
        expect_mock_output = """\
            Called server.HTTPServer(
                %(server_address)r,
                <class '...HTTPRequestHandler'>,
                <gracie.server.GracieServer object ...>)
            """ % vars()
        instance = self.server_class(**params['args'])
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_server_has_openid_server(self):
        """ GracieServer should have an openid_server attribute """
        params = self.valid_servers['simple']
        instance = params['instance']
        openid_server = instance.openid_server
        self.failUnless(isinstance(openid_server, Stub_OpenIDServer))

    def test_openid_store_created_with_datadir(self):
        """ OpenIDStore should be created with specified datadir """
        params = self.valid_servers['datadir']
        datadir = params['datadir']
        scaffold.mock(
            "server.OpenIDStore", tracker=self.mock_tracker)
        expect_mock_output = """\
            Called server.OpenIDStore(%(datadir)r)
            """ % vars()
        instance = self.server_class(**params['args'])
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_server_has_auth_service(self):
        """ GracieServer should have an auth_service attribute """
        params = self.valid_servers['simple']
        instance = params['instance']
        auth_service = instance.auth_service
        self.failIfIs(None, auth_service)

    def test_server_has_session_manager(self):
        """ GracieServer should have a sess_manager attribute """
        params = self.valid_servers['simple']
        instance = params['instance']
        sess_manager = instance.sess_manager
        self.failIfIs(None, sess_manager)

    def test_server_has_authorisation_store(self):
        """ GracieServer should have a consumer_auth_store attribute """
        params = self.valid_servers['simple']
        instance = params['instance']
        consumer_auth_store = instance.consumer_auth_store
        self.failIfIs(None, consumer_auth_store)

    def test_serve_forever_is_callable(self):
        """ GracieServer.serve_forever should be callable """
        self.failUnless(callable(self.server_class.serve_forever))
