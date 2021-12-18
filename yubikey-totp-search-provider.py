#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This file is part of gnome-search-yubikey-totp.

gnome-search-yubikey-totp is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

gnome-search-yubikey-totp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""

import subprocess

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
from gi.repository import GLib

DBusGMainLoop(set_as_default=True)

# Convenience shorthand for declaring dbus interface methods.
# s.b.n. -> search_bus_name
search_bus_name = "org.gnome.Shell.SearchProvider2"
sbn = dict(dbus_interface=search_bus_name)


class SearchPassService(dbus.service.Object):
    """The search daemon.
    This service is started through DBus activation by calling the
    :meth:`Enable` method, and stopped with :meth:`Disable`.
    """

    bus_name = "name.haavard.Yubikey.SearchProvider"

    _object_path = "/" + bus_name.replace(".", "/")

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)

    @dbus.service.method(in_signature="sasu", **sbn)
    def ActivateResult(self, id, terms, timestamp):
        subprocess.run(["yubikey-totp-copy-code.py", "".join(terms[1:])])

    @dbus.service.method(in_signature="as", out_signature="as", **sbn)
    def GetInitialResultSet(self, terms):
        return self.get_result_set(terms)

    @dbus.service.method(in_signature="as", out_signature="aa{sv}", **sbn)
    def GetResultMetas(self, ids):
        return [dict(id=id, name=id, gicon="com.yubico.yubioath") for id in ids]

    @dbus.service.method(in_signature="asas", out_signature="as", **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        return self.get_result_set(new_terms)

    @dbus.service.method(in_signature="asu", terms="as", timestamp="u", **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

    def get_result_set(self, terms):
        if len(terms) > 1 and terms[0] in ("code", "mfa", "totp"):
            name = "".join(terms[1:])
            return [f"Get oauth code for {name}"]
        else:
            return []


def main():
    SearchPassService()
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
