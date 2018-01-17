#!/usr/bin/python3
# coding: utf-8
#
# A simple indicator applet displaying cpu and memory information
# for the budgie-desktop
#
# Author: fossfreedom <foss.freedom@gmail.com>
# Original Homepage: http://launchpad.net/indicator-sysmonitor
# Homepage: https://github.com/fossfreedom/indicator-sysmonitor
# License: GPL v3
#
from gettext import gettext as _
from gettext import textdomain, bindtextdomain
import gi
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, GLib, Gdk
import sys
import os
import logging
import tempfile
from threading import Event, Thread
import gdax
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


logging.basicConfig(level=logging.INFO)


class IndicatorSysmonitor(object):
    SENSORS_DISABLED = False

    def __init__(self):
     
        self.label = Gtk.Label.new()
        self.label.set_name("test")
        self.tmpl = "%s %.2f <span color='%s'>%s %.1f%%</span>"
        

        self.public_client = gdax.PublicClient()
        
        
        self.thd = Thread(target=self.thread)
        self.thd.isDaemon = True
        self.thd.start()
        
    def thread(self):
        data = self.public_client.get_product_24hr_stats('BTC-USD')
        last = float(data["last"])
        while 1:
            try:
                data = self.public_client.get_product_24hr_stats('BTC-USD')
       
                perc = -(100-(last/float(data["open"]))*100)
                color = "red" if perc < 0 else "green"
                if color == "red":
                    symbol = "▼"
                else:
                    symbol = "▲"
                    
                s = self.label.get_style_context()
                
                GLib.idle_add(s.remove_class, "tick-green")
                GLib.idle_add(s.remove_class, "tick-red")
                
                if float(data["last"]) != last:
                    #print("add class")
                    if float(data["last"]) < last:
                        GLib.idle_add(s.add_class, "tick-red")
                    else:
                        GLib.idle_add(s.add_class, "tick-green")
                      
                last = float(data["last"])
                GLib.idle_add(self.label.set_markup, self.tmpl % ("฿ ", last, color, symbol, perc))
                
                #print(data)
                time.sleep(10)
            except:
                time.sleep(10)
                GLib.idle_add(self.label.set_markup, "Failed to fetch BTC")
                continue



class BudgieCrypto(GObject.Object, Budgie.Plugin):
    """ This is simply an entry point into the SysMonitor applet
        Note you must always override Object, and implement Plugin.
    """

    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "BudgieCrypto"

    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return BudgieCryptoApplet(uuid)

class BudgieCryptoApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """

    button = None

    def __init__(self, uuid):
        Budgie.Applet.__init__(self)
        
        css = Gtk.CssProvider()
        self.uuid = uuid

        # css.load_from_file(file)
        b = b"""
            @keyframes spin {
              0% { background-color: initial; }
              50% { background-color: #00ff00; } 
              100% { background-color: initial; }
            }
            @keyframes spin-red {
              0% { background-color: initial; }
              50% { background-color: #ff0000; } 
              100% { background-color: initial; }
            }
            .tick-green {
              animation-name: spin;
              animation-duration: 1s;
              animation-timing-function: linear;
              animation-iteration-count: 3;
            }
            .tick-red {
              animation-name: spin-red;
              animation-duration: 1s;
              animation-timing-function: linear;
              animation-iteration-count: 3;
            }
            #test {
                padding-left: 5px;
                padding-right: 5px;
            }
        """

        css.load_from_data(b)

        Gtk.StyleContext.add_provider_for_screen(
           Gdk.Screen.get_default(),
           css,
           Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Add a button to our UI
        logging.info("start")


        self.app = IndicatorSysmonitor()
        self.button = self.app.label

        self.add(self.button)
        self.show_all()
