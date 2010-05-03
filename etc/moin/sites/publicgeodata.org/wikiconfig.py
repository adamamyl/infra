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

    show_timings = 1

    # basic options (you normally need to change these)
    sitename = u'Public Geo Data' # [Unicode]
    interwikiname = 'Public Geodata'
    page_front_page = u'FrontPage'

    theme_default = 'geo'
    theme_force = True
    page_front_page = 'Home'

# added by jwalsh 03-02-2006
# modified by zoobab 18-02-2006@2am
# modified by rgrp 20-02-2006 to put in WhatIsInspire link and redo What To Do
    navi_bar = [
        u'[[Home|Home]]',
        u'[[WhatIsInspire|What is INSPIRE]]',
        u'[[InspireTimeline|Timeline]]',
        u'[[Arguments|Arguments]]',
        u'[[ActOnInspire|What To Do]]',
        u'[[Banners|Banners]]',
        u'[[Forums|Forums]]',
        u'[[AboutThisCampaign|About]]',
       ]

# added by jwalsh 2006-02-21
    allowed_actions = ['AttachFile']
    attachments = {
    	'dir':'/var/www/publicgeodata.org/files/',
	'url':'/files/',
	}

# added by jwalsh 2006-03-29
    acl_enabled = 1
    acl_rights_default = "All:read"
    #acl_rights_before = "JoWalsh,BenjaminHenrion,RufusPollock:admin"
