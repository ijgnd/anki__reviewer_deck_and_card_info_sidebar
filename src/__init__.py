"""
This is a very extended  modification of glutanimates
[Extended Card stats during review](https://ankiweb.net/shared/info/1008566916) (ECDR).
This modification adds some info I find interesting and hides other content and
adds some support for the night mode add-on.

copyright (c) 2018- ijgnd

other authors:
- (c) Ankitects Pty Ltd and contributors
- (c) Glutanimate 2015-2018
- (c) Lovac42 2018-
- (c) Steve AW 2013
- (c) hssm

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


This add-on incorporates or slightly modifies many functions from the anki source and these add-ons
- [Extended Card stats during review](https://ankiweb.net/shared/info/1008566916)
- [Advanced Browser](https://ankiweb.net/shared/info/874215009)
- [Warrior Mode - Stats & Debug](https://ankiweb.net/shared/info/4241959)
- [Card Info During Review](https://ankiweb.net/shared/info/2179254157)
- [reviewer_show_cardinfo](https://github.com/steveaw/anki_addons/)
- [Open 'Added Today' from Reviewer](https://ankiweb.net/shared/info/861864770)


STRUCTURE OF THIS ADD-ON

- consts.py, config.py
    returns config, taken from Frozen Fields add-on
- card_deck_properties.py
    contains a function that returns properties for a card and its deck
- sidebar_base.py
    for managing the sidebar. contains unmodified functions from ECDR
- cardstats.py
    contains functions that return a short or long table containig important
    card properties
- deckoptions.py
    contains functions that return a short or long table containig important
    deck properties
- helper_functions.py
    contains various function used in cardstats.py and deckoptions.py
- revlog.py
    contains a function that returns a table with the revlog for a card
- schedulercomparison.py
    most likely irrelevant for you. contains a function that returns a table
    that compares Anki's scheduler with a modification I use
- styling.css
    css that is applied to the sidebar
- sidebar_set_contents.py
    contains a function that determines what is shown in the sidebar. Uses
    output from cardstats.py, deckoptions.py, revlog.py, schedulercomparison.py
"""

from aqt.gui_hooks import (
    profile_did_open,
    profile_will_close,
    state_did_change,
)
from aqt import mw
from aqt.qt import (
    QAction,
    QKeySequence,
)

from .config import gc
from .sidebar_base import StatsSidebar
from .toolbar import get_menu


cs = StatsSidebar(mw)


if gc("open on first review after start"):
    sidebar_visibility = True
else:
    sidebar_visibility = False


def maybe_restore_sidebar(new_state, old_state):
    if new_state == "review" and sidebar_visibility:
        cs.show()
state_did_change.append(maybe_restore_sidebar)  # noqa


# not necessary because of hooks StatsSidebar
# def store_sidebar_visibility(new_state, old_state):
# gui_hooks.state_will_change.append(store_sidebar_visibility)


def card_stats(on):
    global sidebar_visibility
    cs.toggle()
    sidebar_visibility ^= True


alreadyrun = False
def main_setup_menus():  # noqa
    global alreadyrun
    if alreadyrun:
        return
    alreadyrun = True

    view = get_menu(mw, "&View")

    action = QAction(mw)
    action.setText("Card Stats")
    action.setCheckable(True)
    action.setChecked(sidebar_visibility)
    action.setShortcut(QKeySequence("Shift+C"))
    view.addAction(action)
    action.toggled.connect(card_stats)
profile_did_open.append(main_setup_menus)  # noqa


def hide_sidebar():
    global sidebar_visibility
    cs.hide()
profile_will_close.append(hide_sidebar)  # noqa
