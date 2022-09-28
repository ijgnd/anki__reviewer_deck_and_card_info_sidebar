import aqt
from aqt import mw

from .card_deck_properties import current_card_deck_properties
from .cardstats import (
    card_stats_as_in_browser,
    mini_card_stats,
    mini_card_stats_with_ord
)
from .deckoptions import long_deck_options, text_for_short_options
from .schedulercomparison import text_for_scheduler_comparison
from .config import anki_21_version, gc
from .helper_functions import (
    deck_name_and_source_for_filtered,
    number_of_cards_studied_today,
    sidebar_style,
)
from .revlog import revlog_data_mod

import os

def style_script_path() -> str:
    """Returns path to the script that adjusts the last card table style

    Returns
    -------
    string
        The absolute path to the script
    """
    dir_path = os.path.dirname(__file__)
    return os.path.join(dir_path, 'adjust_styles.js')

def style_script_contents() -> str:
    """Returns the content of a JavaScript that adjusts the last card table style

    Returns
    -------
    string
        The contents of the script file
    """
    script_path = style_script_path()
    with open(script_path) as file:
        data = file.read()
    return data


def update_contents_of_sidebar(self):
    if not self.shown:
        return
    txt = ""
    card = self.mw.reviewer.card
    if card:
        if gc('show total cards studied today'):
            total_today_unique, total_today = number_of_cards_studied_today()
            txt += f'<div style="font-size:85%; text-align:left;"><b>{total_today_unique} ({total_today})</b> unique/total cards studied today.</div>'

        p = current_card_deck_properties(card)

        txt += "<h3>Current Card</h3>"

        if gc('try_to_show_origvmod_scheduler') and anki_21_version < 40:
            # txt += '<h4>Scheduler Comparison</h4>'
            txt += text_for_scheduler_comparison(card, p)
            txt += "<hr>"

        # txt += "<h4>Deck Options</h4>"
        if gc('deck_options', "brief") == "brief":
            txt += text_for_short_options(card, p)
            txt += "<hr>"

        if gc('show_deck_names', True):
            txt += deck_name_and_source_for_filtered(card, p)

        if gc('deck_options', "brief") == "long":
            txt += long_deck_options(card, p)

        if gc('card_stats') == "detailed":
            txt += card_stats_as_in_browser(card, p)
        elif gc('card_stats') == "brief_with_ord":
            txt += mini_card_stats_with_ord(card, p, True)
        else:
            txt += mini_card_stats(card, p, True)
        txt += "<p>"
        txt += revlog_data_mod(self, card, gc('num_of_revs', 3))

    try:
        lc = self.mw.reviewer.lastCard()
    except:
        lc = None
    if lc:
        txt += "<hr>"
        txt += "<h3>Last Card</h3>"
        if gc('show_detailed_card_stats_for_current_card'):
            txt += self.mw.col.cardStats(lc)
        else:
            lp = current_card_deck_properties(lc)
            txt += mini_card_stats(lc, lp, False)
        txt += "<p>"
        txt += revlog_data_mod(self, lc, gc('num_of_revs', 3))
    if mw.state != 'review':
        txt = "No Card"
    if aqt.theme.theme_manager.get_night_mode():   # self.night_mode_on:
        style = sidebar_style("styling_dark.css")
    else:
        style = sidebar_style("styling.css")
    # add contents of our adjustment script
    style_adj_script = style_script_contents()
    self.web.setHtml("""
<html>
<head>
<style>
%s
</style>
</head>
<body>
<center>
%s
</center>
<script>%s</script>
</body>
</html>""" % (style, txt, style_adj_script))
