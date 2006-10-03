# -*- coding: iso-8859-1 -*-
# IMPORTANT! This encoding (charset) setting MUST be correct! If you live in a
# western country and you don't know that you use utf-8, you probably want to
# use iso-8859-1 (or some other iso charset). If you use utf-8 (a Unicode
# encoding) you MUST use: coding: utf-8
# That setting must match the encoding your editor uses when you modify the
# settings below. If it does not, special non-ASCII chars will be wrong.

"""
This is a sample config for a wiki that isn't part of a farm but does use
farmconfig for common stuff. Here we define what has to be different from
the farm's common settings.
"""
# Need to set the path since file will be installed in wiki instance dir
import sys
sys.path.insert(0, '/etc/moin')
# we import the FarmConfig class for common defaults of our wikis:
from farmconfig import FarmConfig

# now we subclass that config (inherit from it) and change what's different:
class Config(FarmConfig):

    show_timings = 0

    # basic options (you normally need to change these)
    sitename = u'Free Culture UK' # [Unicode]
    interwikiname = 'MoinMaster'
    # data_dir = './data/'
    acl_rights_default = '+RufusPollock:admin Known:read,write,delete,revert All:read'

    theme_default = 'fcuk'
    theme_force = True
    navi_bar = [ u'[FrontPage Home]',
                 u'[GetInvolved Get Involved]',
                 u'[projects Projects]',
                 u'[FindPage Search]',
                 u'[RecentChanges Recent Changes]',
    ]