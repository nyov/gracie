=======
gracied
=======

------------------------------------
local-authentication OpenID provider
------------------------------------

:Author: |author|
:Date: 2009-12-27
:Copyright: GNU General Public License, version 2 or later
:Manual section: 8
:Manual group: Gracie OpenID provider

..  |command| replace:: gracied

SYNOPSIS
========

|command| --data-dir `DIR` --host `HOST` --port `PORT` --log-level `LEVEL`

DESCRIPTION
===========

This manual page documents briefly the |command| command.

|command| is the Gracie server program. It runs an OpenID provider
service for local system users, and allows those users to authenticate
against the local PAM system via a web interface.

OPTIONS
=======

--help, -h
    Show summary of options.

--version, -v
    Show version of program.

--data-dir `DIR`
    Use `DIR` as the directory to store server state files.
    Default: current directory.

--host `HOST`
    Listen for connections on host address `HOST`.
    Default: localhost.

--port `PORT`
    Listen for connections on port `PORT`.
    Default: http (port 80).

--log-level `LEVEL`
    Set the log message threshold to `LEVEL`.
    Default: WARN.

SEE ALSO
========

The OpenID project page <http://openid.net/>_.

HISTORY
=======

This manual page was written by |author|.

..  |author| replace:: |authorname| |authoremail|
..  |authorname| replace:: Ben Finney
..  |authoremail| replace:: <ben+python@benfinney.id.au>


..
    Local variables:
    coding: utf-8
    mode: rst
    time-stamp-format: "%:y-%02m-%02d"
    time-stamp-start: "^:Date:[ 	]+"
    time-stamp-end: "$"
    time-stamp-line-limit: 20
    End:
    vim: fileencoding=utf-8 filetype=rst :
