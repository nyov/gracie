# -*- coding: utf-8 -*-

# tests/test_httpresponse.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for httpresponse module.
    """

import sys
from StringIO import StringIO

import scaffold
from scaffold import Mock
from test_server import (
    Stub_ResponseHeader,
    )

from gracie import httpresponse


class ResponseHeader_TestCase(scaffold.TestCase):
    """ Test cases for ResponseHeader class. """

    def setUp(self):
        """ Set up test fixtures """

        self.header_class = httpresponse.ResponseHeader

        self.valid_headers = {
            'simple': dict(
                code = 200,
                ),
            'ok': dict(
                code = 200,
                ),
            'ok-protocol': dict(
                code = 200,
                protocol = "HTTP/1.1",
                ),
            'content-type-bogus': dict(
                code = 200,
                content_type = "BoGuS",
                ),
            }

        for key, params in self.valid_headers.items():
            args = params.get('args', dict())
            code = params['code']
            args['code'] = code
            protocol = params.get('protocol')
            if protocol is not None:
                args['protocol'] = protocol
            content_type = params.get('content_type')
            if content_type is not None:
                args['content_type'] = content_type
            params['args'] = args
            instance = self.header_class(**args)
            params['instance'] = instance

    def test_instantiate(self):
        """ New ResponseHeader instance should be created """
        for params in self.valid_headers.values():
            instance = params['instance']
            self.failIfIs(None, instance)

    def test_code_as_specified(self):
        """ ResponseHeader should have specified status code """
        for params in self.valid_headers.values():
            code = params['code']
            instance = params['instance']
            self.failUnlessEqual(code, instance.code)

    def test_protocol_default_http_1_0(self):
        """ ResponseHeader protocol should default to HTTP/1.0 """
        params = self.valid_headers['simple']
        instance = params['instance']
        protocol = "HTTP/1.0"
        self.failUnlessEqual(protocol, instance.protocol)

    def test_protocol_as_specified(self):
        """ ResponseHeader should have specified response protocol """
        for params in self.valid_headers.values():
            protocol = params.get('protocol')
            if protocol is None:
                continue
            instance = params['instance']
            self.failUnlessEqual(protocol, instance.protocol)

    def test_content_type_default_xhtml(self):
        """ ResponseHeader should default to Content-Type of XHTML """
        params = self.valid_headers['simple']
        instance = params['instance']
        expect_field =("Content-Type", "application/xhtml+xml")
        self.failUnless(expect_field in instance.fields)

    def test_content_type_as_specified(self):
        """ ResponseHeader should have specified Content-Type field """
        for params in self.valid_headers.values():
            content_type = params.get('content_type')
            expect_field = ("Content-Type", content_type)
            if content_type is None:
                continue
            instance = params['instance']
            self.failUnless(expect_field in instance.fields)


class Stub_RequestHandler(object):
    """ Stub class for BaseHTTPRequestHandler """

    def __init__(self):
        self.wfile = StringIO("")
    def send_response(self, code, message=None):
        pass
    def end_headers(self):
        pass

class Response_TestCase(scaffold.TestCase):
    """ Test cases for Response class. """

    def setUp(self):
        """ Set up test fixtures """
        self.mock_tracker = scaffold.MockTracker()

        self.response_class = httpresponse.Response

        self.valid_responses = {
            'simple': dict(
                header = Stub_ResponseHeader(code = 200),
                ),
            'payload': dict(
                header = Stub_ResponseHeader(code = 200),
                data = object(),
                ),
            }

        for key, params in self.valid_responses.items():
            args = params.get('args', dict())
            header = params['header']
            args['header'] = header
            data = params.get('data')
            if data is not None:
                args['data'] = data
            params['args'] = args
            instance = self.response_class(**args)
            params['instance'] = instance

    def test_initialise(self):
        """ New Response instance should be created """
        for params in self.valid_responses.values():
            instance = params['instance']
            self.failIfIs(None, instance)

    def test_header_as_specified(self):
        """ Response should have specified header """
        for params in self.valid_responses.values():
            header = params['header']
            instance = params['instance']
            self.failUnlessEqual(header, instance.header)

    def test_data_as_specified(self):
        """ Response should have specified data """
        params = self.valid_responses['payload']
        data = params['data']
        instance = params['instance']
        self.failUnlessEqual(data, instance.data)

    def test_send_to_handler_uses_handler(self):
        """ Response.send_to_handler should use specified handler """
        for params in self.valid_responses.values():
            instance = params['instance']
            handler = Mock(
                'HTTPRequestHandler',
                tracker=self.mock_tracker)
            instance.send_to_handler(handler)
            expect_mock_output = """\
                Called HTTPRequestHandler.send_response(...)
                ...Called HTTPRequestHandler.end_headers()
                Called HTTPRequestHandler.wfile.write(...)
                Called HTTPRequestHandler.wfile.close()
                """
            self.failUnlessMockCheckerMatch(expect_mock_output)
