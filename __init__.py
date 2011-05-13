#encoding:utf-8

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from BeautifulSoup import BeautifulSoup
from gettext import gettext as _
from xl import event
from xl import providers
from xlgui import panel
import config
import gtk
import os
import urllib2 
import webkit

WIKIPANEL = None

def enable(exaile):
    """ """
    if (exaile.loading):
        event.add_callback(_enable, 'exaile_loaded')
    else:
        _enable(None, exaile, None)

def disable(exaile):
    """ """
    global WIKIPANEL
    exaile.gui.remove_panel(WIKIPANEL._child)

def _enable(eventname, exaile, nothing):
    global WIKIPANEL 
    WIKIPANEL = WikiPanel(exaile.gui.main.window)
    exaile.gui.add_panel(*WIKIPANEL.get_panel())    

 
class BrowserPage(webkit.WebView, providers.ProviderHandler):
    """ """
    refresh_script = '''document.getElementById("%s").innerHTML="%s";onPageRefresh("%s");''';
    history_length = 6

    def __init__(self, builder):
        webkit.WebView.__init__(self)
        providers.ProviderHandler.__init__(self, "context_page")
        event.add_callback(self.get_wikipedia_info, 'playback_track_start')
        self.get_settings().set_property('enable-developer-extras', True)

        self.builder = builder

        # XXX: Not yet sure whether the signal handling must happen in the
        # panel, browserpage or somewhere else?
        self.builder.connect_signals({
            'refreshbutton_clicked' : self.refreshbutton_clicked,
            'addressbar_release' : self.addressbar_release,
            'addressbar_activated' : self.addressbar_activated,
        })

    def get_wikipedia_info(self, type, player, track):
        """ """
        # locale = self.exaile.settings.get_str('wikipedia_locale', 'en')
        locale = 'en'
        artist = track.get_tag_display('artist')
        url = "http://%s.wikipedia.org/wiki/%s" % (locale, artist)
        url = url.replace(" ", "_")
        headers = { 'User-Agent' : config.USER_AGENT }
        req = urllib2.Request(url, None, headers)
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read())
        content = soup.find("div", {"id": "content"})
        self.load_html_string(str(content) , url)


    def refreshbutton_clicked(self, button):
        import pdb; pdb.set_trace()
        self._browser.get_wikipedia_info()

    def addressbar_release(self, button):
        """ """
        pass
        
    def addressbar_activated(self, button):
        """ """
        pass


class WikiPanel(panel.Panel):
    """ """
    # Specifies the path to the gladefile (must be in Gtk.Builder format) 
    # and the name of the Root Element in the gladefile
    # ui_info = (os.path.dirname(__file__) + "/data/gui.glade", 'WikiPanelWindow')
    ui_info = (os.path.dirname(__file__) + "/data/wikipanel.ui", 'WikiPanelWindow')

    def __init__(self, parent):
        panel.Panel.__init__(self, parent)
        self.parent = parent
        # This is the name that will show up on the tab in Exaile
        self.name = "Wikipedia" 
        # Typically here you'd set up your gui further, eg connect methods 
        # to signals etc
        self._browser = BrowserPage(self.builder)
        self.setup_widgets()
 
 
    def setup_widgets(self):
        self._scrolled_window = gtk.ScrolledWindow()
        self._scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.add(self._browser)
        frame = self.builder.get_object('RenderingFrame')
        self._scrolled_window.show_all()
        frame.add(self._scrolled_window)
        
