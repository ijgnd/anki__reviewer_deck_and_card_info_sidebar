# -*- coding: utf-8 -*-


from anki.stats import CardStats


from .config import local_conf
from .card_deck_properties import current_card_deck_properties_as_namedtuple
from .cardstats import *
from .deckoptions import *
from .schedulercomparison import *


def update_contents_of_sidebar(self):
    from .revlog import revlogData_mod

    if not self.shown:
        return
    txt = ""
    card = self.mw.reviewer.card
    if card:
        p = current_card_deck_properties_as_namedtuple(card)   

        txt += _("<h3>Current Card</h3>")

        if local_conf.get('try_to_show_origvmod_scheduler',False):
            #txt += _('<h4>Scheduler Comparison</h4>')
            txt += text_for_scheduler_comparison(card, p)
            txt += "<hr>"

        #txt += _("<h4>Deck Options</h4>")  
        if local_conf.get('deck_options',"brief") == "brief": 
            txt += text_for_short_options(card,p)
            txt += "<hr>"

        if local_conf.get('show_deck_names',True):
            txt += deck_name_and_source_for_filtered(card,p)

        if local_conf.get('deck_options',"brief") == "long":
            txt += long_deck_options(card,p)

        if local_conf.get('show_detailed_card_stats_for_current_card',False):
            txt += card_stats_as_in_browser(card,p)
        else:
            txt += mini_card_stats(card, p, True)
        txt += "<p>"
        txt += revlogData_mod(self, card, local_conf.get('num_of_revs',3))

    lc = self.mw.reviewer.lastCard()
    if lc:
        txt += "<hr>"
        txt += _("<h3>Last Card</h3>")
        if local_conf.get('show_detailed_card_stats_for_current_card',False):
            txt += self.mw.col.cardStats(lc)
        else:
            lp = current_card_deck_properties_as_namedtuple(lc) 
            txt += mini_card_stats(lc, lp, False)
        txt += "<p>"
        txt += revlogData_mod(self, lc, local_conf.get('num_of_revs',3))
    if mw.state!='review':
        txt = _("No Card")
    style = sidebar_style()
    self.web.setHtml("""
<html><head>
</head><style>%s</style>
<body><center>%s</center></body></html>"""% (style, txt))

