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
from xl import settings
from xl import main as ex
from xl import providers
from xlgui import panel
import config
import gtk
import logging
import os
import urllib2 
import webkit
import preferences

log = logging.getLogger('exaile-wikipedia/__init__.py')

WIKIPANEL = None
CURPATH = os.path.realpath(__file__)
BASEDIR = os.path.dirname(CURPATH)+os.path.sep

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

def get_preferences_pane():
    return preferences 

class WebPage(object):
    """ """

    def __init__(self, html, url):
        self.html = html
        self.url = url
        
 
class BrowserPage(webkit.WebView, providers.ProviderHandler):
    """ """
    refresh_script = '''document.getElementById("%s").innerHTML="%s";onPageRefresh("%s");''';
    history_length = 6

    def __init__(self, builder):
        webkit.WebView.__init__(self)
        providers.ProviderHandler.__init__(self, "context_page")
        event.add_callback(self.on_playback_start, 'playback_track_start')
        self.get_settings().set_property('enable-developer-extras', True)

        self.homepage = None
        self.builder = builder

        self.setup_buttons()

    def setup_buttons(self):
        self.prev_button = self.builder.get_object('PrevButton')
        self.prev_button.set_tooltip_text('Previous')
        self.prev_button.set_sensitive(False)
        self.prev_button.connect('clicked', self.on_prev_clicked)

        self.next_button = self.builder.get_object('NextButton')
        self.next_button.set_tooltip_text('Next')
        self.next_button.set_sensitive(False)
        self.next_button.connect('clicked', self.on_next_clicked)

        self.home_button = self.builder.get_object('HomeButton')
        self.home_button.set_tooltip_text('Home')
        self.home_button.connect('clicked', self.on_home_clicked)

        self.refresh_button = self.builder.get_object('RefreshButton')
        self.refresh_button.set_tooltip_text('Refresh')
        self.refresh_button.connect('clicked', self.on_refresh_page)
        self.refresh_button_image = self.builder.get_object('RefreshButtonImage')

        self.refresh_animation = gtk.gdk.PixbufAnimation(BASEDIR+'loader.gif')


    def on_playback_start(self, type, player, track):
        self.hometrack = track
        self.load_wikipedia_page(track)


    def on_refresh_page(self, widget=None,param=None):
        track = ex.exaile().player._get_current()
        self.load_wikipedia_page(track)


    def on_home_clicked(self, widget=None,param=None):
        self.load_wikipedia_page(self.hometrack)


    def load_wikipedia_page(self, track):
        artist = track.get_tag_display('artist')
        language = settings.get_option('plugin/wikipedia/language', 'en')
        if language not in config.LANGUAGES:
            log.error('Provided language "%s" not found.' % language)
            language = 'en'

        url = "http://%s.wikipedia.org/wiki/%s" % (language, artist)
        url = url.replace(" ", "_")
        headers = { 'User-Agent' : config.USER_AGENT }
        req = urllib2.Request(url, None, headers)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            log.error(e)
            log.error(
                "Error occured when trying to retrieve Wikipedia page "
                "for %s." % artist)
            html = """
                <p style="color: red">No Wikipedia page found for <strong>%s</strong></p>
                """ % artist
        else:
            soup = BeautifulSoup(response.read())
            soup.find("div", {"id": "mw-page-base"}).extract()
            soup.find("div", {"id": "mw-head-base"}).extract()
            soup.find("div", {"id": "mw-head"}).extract()
            soup.find("div", {"id": "mw-panel"}).extract()
            # Need to change the containing div's id to disable its CSS
            content_div = soup.find("div", {"id": "content"})
            content_div['id'] = 'dummy'
            html = str(soup)

        self.load_html_string(html, url)

    def on_next_clicked(self, widget=None,param=None):
        self.next()

    def on_prev_clicked(self, widget=None,param=None):
        self.prev()



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
        
