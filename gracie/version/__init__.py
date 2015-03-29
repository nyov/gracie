# -*- coding: utf-8 -*-

# gracie/version/__init__.py
# Part of Gracie, an OpenID provider.
#
# Copyright © 2008–2010 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-2’ for details.

""" Version information for the Gracie package. """

from datetime import datetime
version_info = {}
version_info['date'] = str(datetime.now())
version_info['revno'] = '2'

version_info['version_string'] = "0.2.12"

version_short = "%(version_string)s" % version_info
version_full = "%(version_string)s.r%(revno)s" % version_info
version = version_short

author_name = "Ben Finney"
author_email = "ben+python@benfinney.id.au"
author = "%(author_name)s <%(author_email)s>" % vars()

copyright_year_begin = "2007"
date = version_info['date'].split(' ', 1)[0]
copyright_year = date.split('-')[0]
copyright_year_range = copyright_year_begin
if copyright_year > copyright_year_begin:
    copyright_year_range += "–%(copyright_year)s" % vars()

copyright = "Copyright © %(copyright_year_range)s %(author)s" % vars()
license = "GPL-2+"
