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
from gi.repository import Budgie, GObject, GLib
import sys
import os
import logging
import tempfile
from threading import Event

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


logging.basicConfig(level=logging.INFO)


class IndicatorSysmonitor(object):
    SENSORS_DISABLED = False

    def __init__(self):
        self._preferences_dialog = None
        self._help_dialog = None

        self.ind = Gtk.Button.new()
        self.ind.set_label("Init...")

    def popup_menu(self, *args):
        self.popup.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def update_indicator_guide(self):

        guide = self.sensor_mgr.get_guide()

    def update(self, data):
        # data is the dict of all sensors and their values
        # { name, label }

        # look through data and find out if there are any icons to be set
        for sensor in data:
            test_str = data[sensor].lower()
            if "use_icon" in test_str:
                path = data[sensor].split(":")[1]
                print(path)
                self.ind.set_icon_full(path, "")
                # now strip the icon output from data so that it is not displayed
                remaining = test_str.split("use_icon")[0].strip()
                if not remaining:
                    remaining = " "

                data[sensor] = remaining

            if "clear_icon" in test_str:
                self.ind.set_icon_full(self.tindicator, "")

                remaining = test_str.split("clear_icon")[0].strip()
                if not remaining:
                    remaining = " "

                data[sensor] = remaining

        label = self.sensor_mgr.get_label(data)


        def update_label(label):
            self.ind.set_label(label)
            return False
        if label and self.ind:
            GLib.idle_add(update_label, label.strip())

    def load_settings(self):

        self.sensor_mgr.load_settings()
        self.sensor_mgr.initiate_fetcher(self)
        self.update_indicator_guide()

    # @staticmethod
    def save_settings(self):
        self.sensor_mgr.save_settings()

    # actions raised from menu
    def on_preferences_activated(self, event=None):
        """Raises the preferences dialog. If it's already open, it's
        focused"""
        if self._preferences_dialog is not None:
            self._preferences_dialog.present()
            return

        self._preferences_dialog = Preferences(self)
        self._preferences_dialog.run()
        self._preferences_dialog = None

    def on_full_sysmon_activated(self, event=None):
        os.system('gnome-system-monitor &')

    def on_exit(self, event=None, data=None):
        """Action call when the main programs is closed."""
        # cleanup temporary indicator icon
        os.remove(self.tindicator)
        # close the open dialogs
        if self._help_dialog is not None:
            self._help_dialog.destroy()

        if self._preferences_dialog is not None:
            self._preferences_dialog.destroy()

        logging.info("Terminated")
        self.alive.clear()  # DM: why bother with Event() ???

        try:
            Gtk.main_quit()
        except RuntimeError:
            pass

    def _on_help(self, event=None, data=None):
        """Raise a dialog with info about the app."""
        if self._help_dialog is not None:
            self._help_dialog.present()
            return

        self._help_dialog = Gtk.MessageDialog(
            None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, None)

        self._help_dialog.set_title(_("Help"))
        self._help_dialog.set_markup(HELP_MSG)
        self._help_dialog.run()
        self._help_dialog.destroy()
        self._help_dialog = None

class BudgieSysMonitor(GObject.Object, Budgie.Plugin):
    """ This is simply an entry point into the SysMonitor applet
        Note you must always override Object, and implement Plugin.
    """

    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "BudgieSysMonitor"

    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return BudgieSysMonitorApplet(uuid)

class BudgieSysMonitorApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """

    button = None

    def __init__(self, uuid):
        Budgie.Applet.__init__(self)

        # Add a button to our UI
        logging.info("start")


        self.app = IndicatorSysmonitor()
        self.button = self.app.ind
        self.button.set_relief(Gtk.ReliefStyle.NONE)
        self.add(self.button)
        self.show_all()
