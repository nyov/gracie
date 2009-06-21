# -*- coding: utf-8 -*-

# gracie/server.py
# Part of Gracie, an OpenID provider
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Behaviour for OpenID provider server
"""

import os
import logging
from openid.server.server import Server as OpenIDServer
from openid.store.filestore import FileOpenIDStore as OpenIDStore
import daemon

from httprequest import HTTPRequestHandler
from httpserver import HTTPServer
from authservice import PamAuthService as AuthService
from authorisation import ConsumerAuthStore
from session import SessionManager
import version

# Get the Python logging instance for this module
_logger = logging.getLogger("gracie.server")


pidfile_name = "gracied.pid"

def create_pid_file(pid):
    """ Create a PID file with the specified process ID """
    pidfile = open(pidfile_name, 'w')
    pidfile.write("%(pid)d\n" % vars())

def remove_pid_file():
    """ Remove the PID file for this daemon """
    os.remove(pidfile_name)

def become_daemon():
    """ Detach the current process and run as a daemon. """
    daemon_context = daemon.DaemonContext()
    daemon_context.open()


class GracieServer(object):
    """ Server for Gracie OpenID provider service """

    def __init__(self, socket_params, opts):
        """ Set up a new instance """
        self.version = version.version_full
        self.opts = opts
        self._setup_logging()
        server_address = (opts.host, opts.port)
        self.httpserver = HTTPServer(
            server_address, HTTPRequestHandler, self
            )
        self._setup_openid()
        self.auth_service = AuthService()
        self.sess_manager = SessionManager()
        self.consumer_auth_store = ConsumerAuthStore()

    def _setup_openid(self):
        """ Set up OpenID parameters """
        store = OpenIDStore(self.opts.datadir)
        self.openid_server = OpenIDServer(store)

    def __del__(self):
        _logger.info("Exiting Gracie server")

    def _setup_logging(self):
        """ Set up logging for this server """
        server_version = self.version
        _logger.info(
            "Starting Gracie server (version %(server_version)s)"
            % vars()
            )

    def serve_forever(self):
        """ Begin serving requests indefinitely """
        self.httpserver.serve_forever()
