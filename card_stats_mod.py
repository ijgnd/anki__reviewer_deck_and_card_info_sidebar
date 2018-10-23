# -*- coding: utf-8 -*-

"""
This is a small modification of glutanimates Extended Card stats during review.
I made this add-on to check some modifications I made to Anki's scheduler.
This modification adds some info I find interesting and hides other content.
This modification offers some configuration options.

You can also customize a tables shown or add your own: Check the function
`make_two_column_table` and `make_multi_column_table`.

The main function that determines what is shown in the sidebar is 
`_update_contents_of_sidebar`. Inside this function you can get 
card or deck properties from a namedtuple cdp (for details
see the function  current_card_deck_properties_as_namedtuple(self,card)

This add-on is not well-tested. Errors are likely. If you don't know
how to fix those you shouldn't use this add-on. Instead use glutanimate's
well working and extensivly tested original version.

This add-on incorporates some functions from Anki and the Advanced Browser.

glutanimates version has the following comment on top:


    minimal modification of

    Anki Add-on: Card Stats

    Displays stats in a sidebar while reviewing.

    For the most part based on the following add-ons:

    - Card Info During Review by Damien Elmes (https://ankiweb.net/shared/info/2179254157)
    - reviewer_show_cardinfo by Steve AW (https://github.com/steveaw/anki_addons/)

    This version of Card Stats combines the sidebar in Damien's add-on with the extra
    review log info found in Steve AW's add-on.

    Copyright: (c) Glutanimate 2016-2017 <https://glutanimate.com/>
    License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""


############## USER CONFIGURATION START ##############

SHOW_LONG_DECK_OPTIONS = False
SHOW_BRIEF_DECK_OPTONS = True
TRY_TO_SHOW_ORIGvMOD_SCHEDULER = True
SHOW_DETAILLED_CARD_STATS_FOR_CURRENT_CARD = False
HIDE_TIME_COLUMN_FROM_REVLOG = True
NUM_OF_REVS = 3 # how many prior reviews should be shown in table for current and prior card
SHOW_DECK_NAMES = True
HIGHLIGHT_COLORS = True 
LOW_CRITICAL_COLOR = "Red"
HIGH_CRITICAL_COLOR = "Blue"
DECK_NAMES_LENGTH = 40  # if a string is longer it's split up over multiple lines
OPTIONGROUP_NAMES_LENGTH = 20
# example
# IVL_MOD_COLOR_THRESHOLDS = (70,130) 
# anything below 70 would be in LOW_CRITICAL_COLOR, anything over HIGH_CRITICAL_COLOR would be in 
IVL_MOD_COLOR_THRESHOLDS = (70,110)
LAPSE_MOD_COLOR_THRESHOLDS= (30,70) 

CSSSTYLING = """
body {
    background-color: #dedede;
    margin: 8px;
}
p { 
    margin-top: 1em;
    margin-bottom: 1em;
}
h1,h2,h3,h4{
    display: block;
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
}
"""
##############  USER CONFIGURATION END  ##############

import time
import datetime
from collections import namedtuple, OrderedDict

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.webview import AnkiWebView
import aqt.stats
from anki.lang import _
from anki.utils import fmtTimeSpan
from anki.stats import CardStats
from aqt.utils import showInfo


class StatsSidebar(object):
    def __init__(self, mw):
        self.mw = mw
        self.shown = False
        addHook("showQuestion", self._update_contents_of_sidebar)
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)

    def _addDockable(self, title, w):
        class DockableWithClose(QDockWidget):
            closed = pyqtSignal()
            def closeEvent(self, evt):
                self.closed.emit()
                QDockWidget.closeEvent(self, evt)
        dock = DockableWithClose(title, mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable)
        dock.setWidget(w)
        if mw.width() < 600:
            mw.resize(QSize(600, mw.height()))
        mw.addDockWidget(Qt.RightDockWidgetArea, dock)
        return dock

    def _remDockable(self, dock):
        mw.removeDockWidget(dock)

    def show(self):
        if not self.shown:
            class ThinAnkiWebView(AnkiWebView):
                def sizeHint(self):
                    return QSize(200, 100)
            self.web = ThinAnkiWebView()
            self.shown = self._addDockable(_("Card Info"), self.web)
            self.shown.closed.connect(self._onClosed)

        self._update_contents_of_sidebar()

    def hide(self):
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None
            #actionself.mw.form.actionCstats.setChecked(False)

    def toggle(self):
        if self.shown:
            self.hide()
        else:
            self.show()

    def _onClosed(self):
        # schedule removal for after evt has finished
        self.mw.progress.timer(100, self.hide, False)

    #copied from Browser, added IntDate column
    def _revlogData(self, card, cs,limit):
        entries = self.mw.col.db.all(
            "select id/1000.0, ease, ivl, factor, time/1000.0, type "
            "from revlog where cid = ?", card.id)
        if not entries:
            return ""
        s = "<table width=100%%><tr><th align=left>%s</th>" % _("Date")
        s += ("<th align=right>%s</th>" * 5) % (
            _("Type"), _("Rat"), _("Ivl"), "IntDate", _("Ease"))
        if not HIDE_TIME_COLUMN_FROM_REVLOG:
            s += ("<th align=right>%s</th>") % (_("Time"))
        cnt = 0
        limitentries = list(reversed(entries))[:limit]
        for (date, ease, ivl, factor, taken, type) in limitentries:
            cnt += 1
            s += "<tr><td>%s</td>" % time.strftime(_("<b>%Y-%m-%d</b> @ %H:%M"),
                                                   time.localtime(date))
            tstr = [_("Learn"), _("Review"), _("Relearn"), _("Filtered"),
                    _("Resched")][type]
            import anki.stats as st

            fmt = "<span style='color:%s'>%s</span>"
            if type == 0:
                tstr = fmt % (st.colLearn, tstr)
            elif type == 1:
                tstr = fmt % (st.colMature, tstr)
            elif type == 2:
                tstr = fmt % (st.colRelearn, tstr)
            elif type == 3:
                tstr = fmt % ("#3c9690", tstr) # yellow  (st.colCram, tstr)
            else:
                tstr = fmt % ("#000", tstr)
            if ease == 1:
                ease = fmt % (st.colRelearn, ease)
                ####################
            int_due = "na"
            if ivl > 0:
                int_due_date = time.localtime(date + (ivl * 24 * 60 * 60))
                int_due = time.strftime(_("%Y-%m-%d"), int_due_date)
                ####################
            if ivl == 0:
                ivl = _("0d")
            elif ivl > 0:
                ivl = fmtTimeSpan(ivl * 86400, short=True)
            else:
                ivl = cs.time(-ivl)

            s += ("<td align=right>%s</td>" * 5) % (
                tstr,
                ease, ivl,
                int_due
                ,
                "%d%%" % (factor / 10) if factor else "")
            if not HIDE_TIME_COLUMN_FROM_REVLOG:
                s += "<td align=right>%s</td>" % cs.time(taken)
            s += "</tr>"

        s += "</table>"
        if cnt < card.reps:
            s += _("""""")
        return s


    def due_day(self,card):
        if card.queue < 0:
            mydue = None
        else:
            if card.queue in (2,3):
                if card.odue:
                    myvalue = card.odue
                else:
                    myvalue = card.due
                mydue = time.time()+((myvalue - mw.col.sched.today)*86400)
            else:
                if card.odue:
                    mydue = card.odue
                else:
                    mydue = card.due
            return time.strftime("%Y-%m-%d", time.localtime(mydue))


    #from Advanced Browser - overdue_days     
    def valueForOverdue(self, card):
        myvalue=0
        if card.queue == 1:
            return
        elif card.queue == 0 or card.type == 0:
            return
        elif card.odue and (card.queue in (2,3) or (type == 2 and queue < 0)):
            myvalue = card.odue 
        elif card.queue in (2,3) or (card.type == 2 and card.queue < 0):
            myvalue = card.due
        if myvalue:
            diff = myvalue - mw.col.sched.today
            if diff < 0:
                return diff * -1
            else:
                return

    def fmt_long_string(self, name, value):
        l = 0
        u = value
        out = ""
        while l < len(name):
            out += name[l:l+u] + '\n'
            l += u
        return out.rstrip('\n') 

    def fmt_int_as_str__maybe_in_critical_color(self,valueInt, threshold):
        if HIGHLIGHT_COLORS and valueInt <= threshold[0]:
            return "<div style='color: {};'>{} </div>".format(LOW_CRITICAL_COLOR, valueInt)
        elif HIGHLIGHT_COLORS and valueInt >=  threshold[1]:
            return "<div style='color: {};'>{} </div>".format(HIGH_CRITICAL_COLOR,valueInt)
        else:
            return str(valueInt)

    def make_Line_Adjusted(self, k, v,):    #from stats.py
        txt = "<tr><td align=left width='35%' style='padding-right: 3px;'>"
        txt += "<b>%s</b></td><td>%s</td></tr>" % (k, v)
        return txt

    def make_two_column_table(self, d):
        o = OrderedDict(d)
        txt = ""
        txt += "<p> <table width=100%>"  
        for k, v in o.items():
            txt += self.make_Line_Adjusted(k, v)
        txt += "</table></p>" 
        return txt

    def make_TD_Adjusted(self, a):    #from stats.py
        txt = "<td align=left style='padding-right: 3px;'> %s </td>" %a
        print(txt)
        return txt
    
    def make_multicolumn_line_for_table(self, cl):   
        """takes a list of strings and returns formatted"""
        txt = "<tr>" 
        for i in cl:
            txt += self.make_TD_Adjusted(i)
        txt += "</tr>"
        return txt

    def make_multi_column_table(self, *rows):
        txt = "<p> <table width=100%>"
        for r in rows:
            txt += self.make_multicolumn_line_for_table(r)
        txt += "</table></p>"
        return txt

    def deck_name_and_source_for_filtered(self,card,cdp):
        rows = []
        if len(cdp.deckname) > DECK_NAMES_LENGTH:
            rows.append(("Deck:",cdp.deckname_fmt))
        else:
            rows.append(("Deck:",cdp.deckname))
        if card.odid:
            if len(cdp.source_deck_name) > DECK_NAMES_LENGTH:
                rows.append(("Source Deck", cdp.source_deck_name_fmt))
            else:   
                rows.append(("Source Deck", cdp.source_deck_name))
        return self.make_two_column_table(rows)

    def text_for_long_options(self,card,cdp): 
        rows_long_deck_options = [
            ('', ),
            ("Opt Group", cdp.optiongroup),             
            ("Learning Steps", cdp.steps_new_fmt[4:]),
            ("",'   ' +  cdp.steps_new_str),
            ("Graduating Ivl", cdp.GraduatingIvl + ' days'),
            ("Easy Ivl", cdp.EasyIvl + ' days'),
            ("Easy Bonus", cdp.easybonus + '%'),
            ("Ivl Mod", self.fmt_int_as_str__maybe_in_critical_color(cdp.im_int,IVL_MOD_COLOR_THRESHOLDS)),
            ("Lapse NewIvl", self.fmt_int_as_str__maybe_in_critical_color(cdp.lapse_ivl_int, LAPSE_MOD_COLOR_THRESHOLDS)),
            ]
        return self.make_two_column_table(rows_long_deck_options)

    def mini_card_stats(self,card,cdp,showOD):
        rows_mini_stats = [
            ("Ivl days is:",cdp.card_ivl_str),
            ("Ease:",cdp.easefct),
            ("Due day:",cdp.dueday),
            ("cid/card created:", cdp.cid + '&nbsp;&nbsp;--&nbsp;&nbsp;' +  cdp.now),
        ]
        if showOD:
            rows_mini_stats.insert(1,("Overdue days: ",cdp.value_for_overdue))
        return self.make_two_column_table(rows_mini_stats)

    def text_for_scheduler_comparison(self, card, cdp):
        txt= ""
        try: 
            orig_hard_days = mw.col.sched.original_nextRevIvl(card, 2)
        except:
            return txt
        else:
            if orig_hard_days:
                orig_good_days = mw.col.sched.original_nextRevIvl(card, 3)
                orig_easy_days = mw.col.sched.original_nextRevIvl(card, 4)

                hard_days = mw.col.sched._nextRevIvl(card, 2)
                good_days = mw.col.sched._nextRevIvl(card, 3)
                easy_days = mw.col.sched._nextRevIvl(card, 4)

                row1 = ["",
                        "days(h-g-e)",
                        "hard(fmt)",
                        "good(fmt)",
                        "easy(fmt)"]
                row2 = ["<b>orig:</b>", 
                        "{} {} {}".format(orig_hard_days,orig_good_days,orig_easy_days),
                        fmtTimeSpan(orig_hard_days*86400, short=True), 
                        fmtTimeSpan(orig_good_days*86400, short=True),
                        fmtTimeSpan(orig_easy_days*86400, short=True)]
                row3 = ["<b>mod:</b>", 
                        "{} {} {}".format(hard_days,good_days,easy_days),
                        fmtTimeSpan(hard_days*86400, short=True),
                        fmtTimeSpan(good_days*86400, short=True),
                        fmtTimeSpan(easy_days*86400, short=True)]

                return self.make_multi_column_table(row1,row2,row3)

    def text_for_short_options(self,card,cdp): 
        row1 = ["OptGr",
                "Step",
                "GrIv",
                "EaIv",
                "EaBo",
                "IvMo",
                "LpIv"]
        row1_bold = ["<b>" + i + "</b>" for i in row1]
        # option group names can be very long
        if len(cdp.optiongroup) > 15 and DECK_NAMES_LENGTH:
            groupname = cdp.optiongroup_fmt
        else:
            groupname = cdp.optiongroup
        im_colored = self.fmt_int_as_str__maybe_in_critical_color(cdp.im_int,IVL_MOD_COLOR_THRESHOLDS),
        lapse_colored = self.fmt_int_as_str__maybe_in_critical_color(cdp.lapse_ivl_int,LAPSE_MOD_COLOR_THRESHOLDS),
        row2 = [groupname,
                cdp.steps_new_str[1:-1],
                cdp.GraduatingIvl,
                cdp.EasyIvl,
                cdp.easybonus,
                im_colored,
                lapse_colored]
        return self.make_multi_column_table(row1_bold,row2)

    def current_card_deck_properties_as_namedtuple(self,card):
        cdp = namedtuple('CardProps', """
                conf
                cid
                Reviews
                Lapses
                Type
                steps_new_int
                steps_new_str
                steps_new_fmt
                GraduatingIvl
                EasyIvl
                Starting_ease
                new__order_of_new_cards
                new__cards_per_day                
                bury_related_new_cards
                MaxiumReviewsPerDay
                im_int
                im_str
                easybonus
                MaximumInterval
                bury_related_reviews_until_next_day
                lapse_leech_threshold
                lapse_leech_action
                lapse_ivl_int
                lapse_ivl_str
                lapse_mint_int
                lapse_learning_steps
                easefct
                optiongroup
                optiongroup_fmt
                deckname
                deckname_fmt
                source_deck_name
                source_deck_name_fmt
                card_ivl_str
                dueday
                value_for_overdue
                now
                """)

        if card.odid:
            conf=self.mw.col.decks.confForDid(card.odid)
            source_deck_name = aqt.mw.col.decks.get(card.odid)['name']
        else:
            conf=self.mw.col.decks.confForDid(card.did)
            source_deck_name=""

        formatted_steps = ''
        for i in conf['new']['delays']:
            formatted_steps += ' -- ' + fmtTimeSpan(i * 60, short=True)
        
        out = cdp(
                conf=conf,
                cid=str(card.id),
                Reviews=card.reps,
                Lapses=card.lapses,
                Type=card.type,
                steps_new_int=conf['new']['delays'],
                steps_new_str=str(conf['new']['delays']),
                steps_new_fmt=formatted_steps, # self.fmt_long_string(str(conf['new']['delays']),OPTIONGROUP_NAMES_LENGTH),
                GraduatingIvl=str(conf['new']['ints'][0]),
                EasyIvl=str(conf['new']['ints'][1]),
                Starting_ease = conf['new']['initialFactor'] / 10 ,
                new__order_of_new_cards=conf['new']['order'],
                new__cards_per_day=conf['new']['perDay'],
                bury_related_new_cards=conf['new']['bury'],
                MaxiumReviewsPerDay=conf['rev']['perDay'],
                im_int=int(100 * conf['rev']['ivlFct']),
                im_str=str(int(100 * conf['rev']['ivlFct'])),
                easybonus=str(int(100 * conf['rev']['ease4'])),
                MaximumInterval=conf['rev']['maxIvl'],
                bury_related_reviews_until_next_day = conf['rev']['bury'],
                lapse_leech_threshold = conf['lapse']['leechFails'],
                lapse_leech_action  = conf['lapse']['leechAction'],
                lapse_ivl_int=int(100 * conf['lapse']['mult']),
                lapse_ivl_str=str(int(100 * conf['lapse']['mult'])),
                lapse_mint_int=conf['lapse']['minInt'],
                lapse_learning_steps=conf['lapse']['delays'],
                easefct=str(int(card.factor/10.0)),
                optiongroup=conf['name'],
                optiongroup_fmt=self.fmt_long_string(conf['name'],OPTIONGROUP_NAMES_LENGTH),
                deckname=aqt.mw.col.decks.get(card.did)['name'],
                deckname_fmt=self.fmt_long_string(aqt.mw.col.decks.get(card.did)['name'],DECK_NAMES_LENGTH),
                source_deck_name=source_deck_name,
                source_deck_name_fmt=self.fmt_long_string(source_deck_name,DECK_NAMES_LENGTH),
                card_ivl_str=str(card.ivl),
                dueday=str(self.due_day(card)),
                value_for_overdue=str(self.valueForOverdue(card)),
                now=time.strftime('%Y-%m-%d %H:%M', time.localtime(card.id/1000))
        )
        return out


    def _update_contents_of_sidebar(self):
        if not self.shown:
            return
        txt = ""
        cs = CardStats(self.mw.col, self.mw.reviewer.card)
        card = self.mw.reviewer.card
        if card:
            cdp = self.current_card_deck_properties_as_namedtuple(card)   #card-decks-properties

            txt += _("<h3>Current Card</h3>")

            if TRY_TO_SHOW_ORIGvMOD_SCHEDULER:
                #txt += _('<h4>Scheduler Comparison</h4>')
                txt += self.text_for_scheduler_comparison(card, cdp)
                txt += "<hr>"

            #txt += _("<h4>Deck Options</h4>")  
            if SHOW_BRIEF_DECK_OPTONS: 
                txt += self.text_for_short_options(card,cdp)
                txt += "<hr>"

            if SHOW_DECK_NAMES:
                txt += self.deck_name_and_source_for_filtered(card,cdp)

            if SHOW_LONG_DECK_OPTIONS:
                txt += self.text_for_long_options(card,cdp)

            if SHOW_DETAILLED_CARD_STATS_FOR_CURRENT_CARD:
                txt += self.mw.col.cardStats(card)
            else:
                txt += self.mini_card_stats(card, cdp, True)
            txt += "<p>"
            txt += self._revlogData(card, cs, NUM_OF_REVS)

        lc = self.mw.reviewer.lastCard()
        if lc:
            txt += "<hr>"
            txt += _("<h3>Last Card</h3>")
            if SHOW_DETAILLED_CARD_STATS_FOR_CURRENT_CARD:
                txt += self.mw.col.cardStats(lc)
            else:
                txt += self.mini_card_stats(lc, cdp, False)
            txt += "<p>"
            txt += self._revlogData(lc, cs, NUM_OF_REVS)
        if not txt:
            txt = _("No current card or last card.")
        style = self._style()
        self.web.setHtml("""
<html><head>
</head><style>%s</style>
<body><center>%s</center></body></html>"""% (style, txt))
                
    def _style(self):
        from anki import version
        mystyle = CSSSTYLING
        if version.startswith("2.0."):
            return mystyle 
        return mystyle + " td { font-size: 80%; }"

_cs = StatsSidebar(mw)

def cardStats(on):
    _cs.toggle()

action = QAction(mw)
action.setText("Card Stats")
action.setCheckable(True)
action.setShortcut(QKeySequence("Shift+C"))
mw.form.menuTools.addAction(action)
action.toggled.connect(cardStats)
