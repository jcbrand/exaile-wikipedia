import os
from gettext import gettext as _
import xl.plugins as plugins

PLUGIN_NAME = _("Wikipedia")
PLUGIN_AUTHORS = ['JC Brand <jc@opkode.com>', 'Amit Man <amit.man@gmail.com>']
PLUGIN_VERSION = '0.5'
PLUGIN_DESCRIPTION = _(r"""Displays contextual information from Wikipedia.
\n\nPress the 'i' icon the show the popup window. Double click on popup window to hide it.""")
PLUGIN_ENABLED = False

USER_AGENT = '%s/%s (Exaile)' % \
    (PLUGIN_NAME, PLUGIN_VERSION)

# CONNS = plugins.SignalContainer()

## Default module variables
if os.name == "posix":
    LOCALE = "en_FI"
else:
    LOCALE = "en"
ESCAPE = [(".", "_PERIOD_"), (":", "_COLON_")]
