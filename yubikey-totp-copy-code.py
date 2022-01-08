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

import re
import subprocess
import sys
import time

import gi
from fuzzywuzzy import process

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Gdk, Gtk, GLib, Notify


class YubikeyMissingWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Yubikey missing")
        self.set_default_size(150, 100)

        self.label = Gtk.Label(label="Please insert yubikey")
        self.add(self.label)


class YubikeyCode:
    def __init__(self):
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        Notify.init("yubikey-copy-code")
        self.notify = None

    def check_yubikey(self, window=None, initial=False):
        ret = subprocess.run(
            ["ykman", "oath", "code"],
            encoding="utf-8",
            timeout=10,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        if ret.returncode != 0:
            if window is not None:
                window.show_all()
            if initial:
                return False
            return True

        codes = {}
        for line in ret.stdout.split("\n"):
            match = re.match("(.*?) +([0-9]{6,})$", line.strip())
            if match:
                codes[match[1]] = match[2]
        match = process.extractOne(sys.argv[1], codes.keys(), score_cutoff=60)
        if match is None:
            self.notify = Notify.Notification.new(
                "Code not found", f"Could not find code for {sys.argv[1]}"
            )
            self.notify.show()
            timeout = 3000
            GLib.timeout_add(2500, self.notify_clear)
        else:
            self.clipboard.set_text(codes[match[0]], -1)
            self.clipboard.store()
            self.notify = Notify.Notification.new(
                "Code copied", f"Copied code for {match[0]}"
            )
            self.notify.show()
            GLib.timeout_add(3000, self.notify_clear)
            timeout = 15000

        if window is not None:
            window.hide()

        GLib.timeout_add(timeout, self.finish)
        return False

    def notify_clear(self):
        if self.notify is not None:
            self.notify.close()
        return False

    def finish(self):
        Gtk.main_quit()


def main():
    if len(sys.argv) != 2:
        print(f"Usage {sys.argv[0]} name")
        sys.exit(1)

    window = YubikeyMissingWindow()
    window.connect("destroy", Gtk.main_quit)

    yubikey_code = YubikeyCode()
    GLib.idle_add(yubikey_code.check_yubikey, window, True)
    GLib.timeout_add(1000, yubikey_code.check_yubikey, window)

    Gtk.main()


if __name__ == "__main__":
    main()
