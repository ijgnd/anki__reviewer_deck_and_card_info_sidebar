# -*- coding: utf-8 -*-

"""
This is a small modification of glutanimates Extended Card stats during review.
I made this add-on to check some modifications I made to Anki's scheduler.
This modification adds some info I (and a friend) find interesting and hides other content.
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

This add-on incorporates some functions from 
- Anki 
- the add-on [Advanced Browser](https://ankiweb.net/shared/info/874215009)
- the add-on [Warrior Mode - Stats & Debug](https://ankiweb.net/shared/info/4241959)



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
import anki.stats as st
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
            return "<div style='color: {};'>{}</div>".format(LOW_CRITICAL_COLOR, str(valueInt))
        elif HIGHLIGHT_COLORS and valueInt >=  threshold[1]:
            return "<div style='color: {};'>{}</div>".format(HIGH_CRITICAL_COLOR, str(valueInt))
        else:
            return str(valueInt)


    def make_two_column_table(self, d):
        o = OrderedDict(d)
        txt = ""
        txt += "<p> <table width=100%>"  
        for k, v in o.items():     #makeLine from stats.py adjusted
            txt += "<tr><td align=left width='35%' style='padding-right: 3px;'>"
            txt += "<b>%s</b></td><td>%s</td></tr>" % (k, v)
        txt += "</table></p>" 
        return txt


    def make_multi_column_table(self, rowlist):
        """takes a list of lists. Each sublist must have four entries: Value - htmlcode before value - 
        htmlcode after value - alignment """
        txt = "<p> <table width=100%>"
        for r in rowlist:
            txt += "<tr>" 
            for c in r: 
                txt += "<td align='%s' style='padding-right: 3px;'> %s %s %s</td>" % (c[3], c[1], str(c[0]), c[2])
            txt += "</tr>"
        txt += "</table></p>"
        return txt


    def make_multi_column_table_first_row_bold(self, rowlist):
        """takes a list of lists. Each sublist must have two entries: Value - alignment """
        for i, r in enumerate(rowlist):
            for c in r:
                if i == 0:
                    c.insert(1,"<b>")
                    c.insert(2,"</b>")
                else:
                    c.insert(1,"") 
                    c.insert(2,"")
        return self.make_multi_column_table(rowlist)


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


    #from warrior-mode
    def formatIvlString(self, cs, ivl):
        if ivl == 0:
            return _("0d")
        elif ivl > 0:
            return fmtTimeSpan(ivl * 86400, short=True)
        else:
            return cs.time(-ivl)


    def show_info_length_of_sublists(self,lol):
        mystr = ""
        def sublist_length(s):
            out = ""
            for e in s:
                out += str(len(e)) + ' '
            return out
        for l in lol:
            mystr += sublist_length(l) + ' '       
        showInfo(mystr)


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


    #copied from Browser, added IntDate column
    #cleanup inspired by  warrior mode
    def _revlogData_mod(self, card, cs,limit):
        entries = self.mw.col.db.all(
            "select id/1000.0, ease, ivl, factor, time/1000.0, type "
            "from revlog where cid = ?", card.id)
        if not entries:
            return ""

        list_of_rows = []
        
        row1 = [["Date","left"],
                ["Type","right"],
                ["Rat","right"],
                ["Ivl","right"],
                ["IntDate","right"],
                ["Ease","right"],]
        if not HIDE_TIME_COLUMN_FROM_REVLOG:
            row1.append(["Time","right"])
        list_of_rows.append(row1)

        limitentries = list(reversed(entries))[:limit]
        for (date, ease, ivl, factor, taken, type) in limitentries:
            tstr = [_("Lrn"), _("Rev"), _("ReLn"), _("Filt"), _("Resch")][type]
                #Learned, Review, Relearned, Filtered, Defered (Rescheduled)
            
            #COLORIZE LOG TYPE
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

            #COLORIZE EASE
            if ease == 1:
                ease = fmt % (st.colRelearn, ease)
            elif ease == 3:
                ease = fmt % ('navy', ease)
            elif ease == 4:
                ease = fmt % ('darkgreen', ease)

            int_due = "na"
            if ivl > 0:
                int_due_date = time.localtime(date + (ivl * 24 * 60 * 60))
                int_due = time.strftime(_("%Y-%m-%d"), int_due_date)

            ivl = self.formatIvlString(cs, ivl)

            row_n = [[time.strftime("<b>%Y-%m-%d</b>@%H:%M",time.localtime(date)),"left"],
                     [tstr,"right"],
                     [ease,"right"],
                     [ivl,"right"],
                     [int_due,"right"],
                     [factor / 10 if factor else "","right"],]
            if not HIDE_TIME_COLUMN_FROM_REVLOG:
                row_n.append([cs.time(taken),"right"])
            list_of_rows.append(list(row_n))  # copy list

        #self.show_info_length_of_sublists(list_of_rows)
        return  self.make_multi_column_table_first_row_bold(list_of_rows)


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

                row1 = [["","left"],
                        ["days(h-g-e)","left"],
                        ["hard(fmt)","center"],
                        ["good(fmt)","center"],
                        ["easy(fmt)","center"],]
                row2 = [["<b>orig:</b>","left"],
                        ["{} {} {}".format(orig_hard_days,orig_good_days,orig_easy_days),"left"],
                        [fmtTimeSpan(orig_hard_days*86400, short=True),"center"],
                        [fmtTimeSpan(orig_good_days*86400, short=True),"center"],
                        [fmtTimeSpan(orig_easy_days*86400, short=True),"center"],]
                row3 = [["<b>mod:</b>","left"],
                        ["{} {} {}".format(hard_days,good_days,easy_days),"left"],
                        [fmtTimeSpan(hard_days*86400, short=True),"center"],
                        [fmtTimeSpan(good_days*86400, short=True),"center"],
                        [fmtTimeSpan(easy_days*86400, short=True),"center"],]

                #self.show_info_length_of_sublists([row1,row2,row3])
                return self.make_multi_column_table_first_row_bold([row1,row2,row3])


    def text_for_short_options(self,card,cdp): 
        row1 = [["OptGr","left"],
                ["Steps","center"],
                ["GrIv","center"],
                ["EaIv","center"],
                ["EaBo","center"],
                ["IvMo","center"],
                ["LpIv","center"],]
        # option group names can be very long
        if len(cdp.optiongroup) > 15 and DECK_NAMES_LENGTH:
            groupname = cdp.optiongroup_fmt
        else:
            groupname = cdp.optiongroup
        im_colored = self.fmt_int_as_str__maybe_in_critical_color(cdp.im_int,IVL_MOD_COLOR_THRESHOLDS)
        lapse_colored = self.fmt_int_as_str__maybe_in_critical_color(cdp.lapse_ivl_int,LAPSE_MOD_COLOR_THRESHOLDS)
        row2 = [[groupname,"left"],
                [cdp.steps_new_str[1:-1],"center"],
                [cdp.GraduatingIvl,"center"],
                [cdp.EasyIvl,"center"],
                [cdp.easybonus,"center"],
                [im_colored,"center"],
                [lapse_colored,"center"],]
        #self.show_info_length_of_sublists([row1,row2])
        return self.make_multi_column_table_first_row_bold([row1,row2])


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
            txt += self._revlogData_mod(card, cs, NUM_OF_REVS)

        lc = self.mw.reviewer.lastCard()
        if lc:
            txt += "<hr>"
            txt += _("<h3>Last Card</h3>")
            if SHOW_DETAILLED_CARD_STATS_FOR_CURRENT_CARD:
                txt += self.mw.col.cardStats(lc)
            else:
                lcdp = self.current_card_deck_properties_as_namedtuple(lc) 
                txt += self.mini_card_stats(lc, lcdp, False)
            txt += "<p>"
            txt += self._revlogData_mod(lc, cs, NUM_OF_REVS)
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
