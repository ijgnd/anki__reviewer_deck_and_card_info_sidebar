# -*- coding: utf-8 -*-

"""
This file is part of the Frozen Fields add-on for Anki.

Global variables

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import sys
import os
from anki import version

anki20 = version.startswith("2.0.")
sys_encoding = sys.getfilesystemencoding()

if anki20:
    addon_path = os.path.dirname(__file__).decode(sys_encoding)
else:
    addon_path = os.path.dirname(__file__)
