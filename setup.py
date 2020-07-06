#!/usr/bin/env python3
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

from setuptools import setup

setup(name="gnome-search-yubikey-totp",
      version="1.0",
      description="Gnome shell yubikey totp search provider",
      author="Håvard Moen",
      author_email="post@haavard.name",
      url="https://github.com/umglurf/gnome-search-yubikey-totp",
      license="GPL3",
      install_requires=["fuzzywuzzy", "python-Levenshtein", "PyGObject", "yubikey-manager"],
      scripts=["yubikey-totp-search-provider.py", "yubikey-totp-copy-code.py"],
      data_files=[
          ("/usr/local/share/gnome-shell/search-providers", ["name.haavard.Yubikey.SearchProvider.ini"]),
          ("/usr/local/share/dbus-1/services", ["name.haavard.Yubikey.SearchProvider.service"])
          ]
      )
