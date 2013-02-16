"""
    settings
    --------

    All application settings. A single point for environmental variable
    interactions.

"""

import os
import tornado
#import tornado.template
from tornado.options import define, options

from jutil import environment
from jackalope.phrase import NAME


# Make filepaths relative to settings.
path = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

# Tornado
PORT = environment.get_integer(unicode("PORT"))
define("port", default=PORT, help="run on the given port", type=int)

define("config", default=None, help="tornado config file")
define("debug", default=True, help="debug mode")
options.parse_command_line()

MEDIA_ROOT = path(ROOT, 'media')
#TEMPLATE_ROOT = path(ROOT, 'view/templates')
#
# settings dictionary
settings = {}
settings['debug'] = options.debug
settings['static_path'] = MEDIA_ROOT
#settings['cookie_secret'] = (
#        "\xee\x0ec\x9bl\x02\xeb/.\xd4\xeb\xc2(\xb0\xb1\x8a\x0b\xb5[^Tq\xecy")
#settings['xsrf_cookies'] = True
#settings['login_url'] = "/"
#settings['template_loader'] = tornado.template.Loader(TEMPLATE_ROOT)
settings['ui_modules'] = {}

if options.config:
    tornado.options.parse_config_file(options.config)


MAILGUN_API_KEY = environment.get_unicode(unicode("MAILGUN_API_KEY"))
MAILGUN_DOMAIN = environment.get_unicode(unicode("MAILGUN_DOMAIN"))

ENVIRONMENT = environment.get_unicode(unicode("ENVIRONMENT"))
DEFAULT_NAME = unicode("")
if ENVIRONMENT == unicode("PRODUCTION"):
    DEFAULT_NAME = NAME.PRODUCTION
elif ENVIRONMENT == unicode("STAGING"):
    DEFAULT_NAME = NAME.STAGING
elif ENVIRONMENT == unicode("DEV"):
    DEFAULT_NAME = NAME.DEV
