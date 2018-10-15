# -*- coding: utf-8 -*-

"""
minimal modification of glutanimates Extended Card stats during review.
I made this add-on to check some modifications I made to Anki's scheduler.
This modification adds some info I find interesting and hides other content.
These are just quick changes using copy&paste and multicursor. The code is 
now in an ugly and more or less non-maintainable state ...
If you don't have a good reason to use this add-on don't. Use glutanimates
original version.

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
MULTILINE_LONG_OPTION_GROUP_NAMES = True
HIDE_TIME_COLUMN_FROM_REVLOG = True
NUM_OF_REVS = 3 # how many prior reviews should be shown in table for current and prior card
HIGHLIGHT_COLORS = True 
LOW_CRITICAL_COLOR = "Red"
HIGH_CRITICAL_COLOR = "Blue"

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



from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.webview import AnkiWebView
import aqt.stats
import time
import datetime
from anki.lang import _
from anki.utils import fmtTimeSpan
from anki.stats import CardStats


class StatsSidebar(object):
    def __init__(self, mw):
        self.mw = mw
        self.shown = False
        addHook("showQuestion", self._update)
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

        self._update()

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

    #copy and paste from Browser
    #Added IntDate column
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

    def makeLineAdjusted(self, k, v,):    #from stats.py
        txt = "<tr><td align=left width='35%'' style='padding-right: 3px;'>"
        txt += "<b>%s</b></td><td>%s</td></tr>" % (k, v)
        return txt

    def makeLineAdjustedAndBreakLong(self, k, v,):    #from stats.py
        txt = "<tr><td align=left width='35%'' style='padding-right: 3px;'>"
        txt += "<b>%s</b></td><td>%s</td></tr>" % (k, v)
        return txt

    def critical_color(self,valueInt, colorconfig):
            if valueInt <= colorconfig[0]:
                return LOW_CRITICAL_COLOR
            elif valueInt >=  colorconfig[1]:
                return HIGH_CRITICAL_COLOR
            else:
                return ""

    def makeLineAdjusted_with_coloring(self, key, valueInt, colorconfig):    #from stats.py
        if not HIGHLIGHT_COLORS:
            txt = self.makeLineAdjusted(key,str(valueInt))
        else:
            color=self.critical_color(valueInt, colorconfig)
            txt = "<tr><td align=left width='35%'' style='padding-right: 3px;'>"
            txt += '<b>{}</b></td><td><div style="color: {};">{} %</div></td></tr>'.format(key, color, str(valueInt))
        return txt

    def mydue(self,card):
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

    def mini_card_stats(self,card,showOD):
        txt = "<p> <table width=100%>"
        txt += self.makeLineAdjusted("Ivl days is:",str(card.ivl))
        if showOD:
            txt += self.makeLineAdjusted("Overdue days: ",str(self.valueForOverdue(card)))
        txt += self.makeLineAdjusted("Ease:",str(int(card.factor/10.0)))
        txt += self.makeLineAdjusted("Due day:",str(self.mydue(card)))
        cidstring = str(card.id) + '&nbsp;&nbsp;--&nbsp;&nbsp;' +  time.strftime('%Y-%m-%d %H:%M', time.localtime(card.id/1000))
        txt += self.makeLineAdjusted("cid/card created:", cidstring)
        txt += "</table></p>"
        return txt

    def _update(self):
        if not self.shown:
            return
        txt = ""
        r = self.mw.reviewer
        d = self.mw.col
        cs = CardStats(d, r.card)
        cc = r.card
        if cc:


            #ugly hack: I don't know why this sometimes fails
            myerror = 0
            if cc.odid:
                try:
                    conf=d.decks.confForDid(cc.odid)
                except:
                    myerror = 1
            else:
                try:
                    conf=d.decks.confForDid(cc.did)
                except:
                    myerror = 1

            if myerror != 1:     

                newsteps=conf['new']['delays']
                formatted_steps = ''
                for i in newsteps:
                    formatted_steps += ' -- ' + fmtTimeSpan(i * 60, short=True)
                GraduatingIvl=conf['new']['ints'][0]
                EasyIvl=conf['new']['ints'][1]
                im=conf['rev']['ivlFct']
                easybonus=conf['rev']['ease4']
                lnivl=conf['lapse']['mult']
                optiongroup=conf['name']

                if SHOW_LONG_DECK_OPTIONS:
                    txt += _("<h3>Deck Options</h3>")
                    txt += "<p> <table width=100%>"
                    txt += self.makeLineAdjusted("Opt Group", optiongroup)                    
                    txt += self.makeLineAdjusted("Learning Steps", formatted_steps[4:])
                    txt += self.makeLineAdjusted("",'   ' + str(newsteps))
                    txt += self.makeLineAdjusted("Graduating Ivl", str(GraduatingIvl) + ' days')
                    txt += self.makeLineAdjusted("Easy Ivl", str(EasyIvl) + ' days')
                    txt += self.makeLineAdjusted("Easy Bonus", str(int(100 * easybonus)) + '%')
                    txt += self.makeLineAdjusted_with_coloring( "Ivl Mod",      int(100 * im)    , IVL_MOD_COLOR_THRESHOLDS)
                    txt += self.makeLineAdjusted_with_coloring( "Lapse NewIvl", int(100 * lnivl) , LAPSE_MOD_COLOR_THRESHOLDS)
                    txt += "</table></p>" 


                ogv = 0
                ogr = 15
                optiongroup_fmt = ""
                while ogv < len(optiongroup):
                    optiongroup_fmt += optiongroup[ogv:ogv+ogr] + '\n'
                    ogv = ogv+ogr
                optiongroup_fmt = optiongroup_fmt.rstrip('\n') 

                if SHOW_BRIEF_DECK_OPTONS: 
                    txt += _("<h3>Deck Options</h3>")
                    txt += "<p> <table width=100%>"
                    txt += """
                    <tr> 
                        <td align=left style='padding-right: 3px;'><b>OptGr</b></td>
                        <td align=left style='padding-right: 3px;'><b>Step</b></td>
                        <td align=left style='padding-right: 3px;'><b>GrIv</b></td>
                        <td align=left style='padding-right: 3px;'><b>EaIv</b></td>
                        <td align=left style='padding-right: 3px;'><b>EaBo</b></td>
                        <td align=left style='padding-right: 3px;'><b>IvMo</b></td>
                        <td align=left style='padding-right: 3px;'><b>LpIv</b></td>
                    </tr>"""

                    txt += "<tr>" 
                    # option group names can be very long
                    if len(optiongroup) > 15 and MULTILINE_LONG_OPTION_GROUP_NAMES:
                        txt += "<td align=left style='padding-right: 3px;'> %s </td>" % optiongroup_fmt
                    else:
                        txt += "<td align=left style='padding-right: 3px;'> %s </td>" % optiongroup
                    txt += "<td align=left style='padding-right: 3px;'> %s </td>" % str(newsteps)[1:-1]
                    txt += "<td align=left style='padding-right: 3px;'> %s </td>" % str(GraduatingIvl)
                    txt += "<td align=left style='padding-right: 3px;'> %s </td>" % str(EasyIvl)
                    txt += "<td align=left style='padding-right: 3px;'> %s </td>" % str(int(100 * easybonus))
                    txt += '<td align=left style="padding-right: 3px;"> <div style="color: %s;"> %s </div></td>' % ( self.critical_color(int(100 * im),   IVL_MOD_COLOR_THRESHOLDS  ), str(int(100 * im)    ))
                    txt += '<td align=left style="padding-right: 3px;"> <div style="color: %s;"> %s </div></td>' % ( self.critical_color(int(100 * lnivl),LAPSE_MOD_COLOR_THRESHOLDS), str(int(100 * lnivl) ))
                    txt += "</tr>"
                    txt += "</table></p>"


                if TRY_TO_SHOW_ORIGvMOD_SCHEDULER:
                    try: 
                        orig_hard_days = mw.col.sched.original_nextRevIvl(cc, 2)
                    except:
                        pass
                    else:
                        if orig_hard_days:
                            orig_good_days = mw.col.sched.original_nextRevIvl(cc, 3)
                            orig_easy_days = mw.col.sched.original_nextRevIvl(cc, 4)

                            hard_days = mw.col.sched._nextRevIvl(cc, 2)
                            good_days = mw.col.sched._nextRevIvl(cc, 3)
                            easy_days = mw.col.sched._nextRevIvl(cc, 4)
                            
                            txt += "<hr>"
                            txt += _('<h3>Scheduler Comparison</h3>')
                            txt += "<p> <table width=100%>"

                            txt += "<tr>" 
                            txt += "<td align=left style='padding-right: 3px;'> <b></b> </td>" 
                            txt += "<td align=left style='padding-right: 3px;'> days(h-g-e) </td>"
                            txt += "<td align=left style='padding-right: 3px;'> hard(fmt) </td>"
                            txt += "<td align=left style='padding-right: 3px;'> good(fmt) </td>"
                            txt += "<td align=left style='padding-right: 3px;'> easy(fmt) </td>"
                            txt += "</tr>"

                            txt += "<tr>" 
                            txt += "<td align=left style='padding-right: 3px;'> <b>orig:</b> </td>" 
                            txt += "<td align=left style='padding-right: 3px;'> %s - %s - %s </td>" % (orig_hard_days, orig_good_days, orig_easy_days)
                            txt += "<td align=left style='padding-right: 3px;'> %s </td>" % (fmtTimeSpan(orig_hard_days*86400, short=True))
                            txt += "<td align=left style='padding-right: 3px;'> %s </td>" % (fmtTimeSpan(orig_good_days*86400, short=True))
                            txt += "<td align=left style='padding-right: 3px;'> %s </td>" % (fmtTimeSpan(orig_easy_days*86400, short=True))
                            txt += "</tr>"

                            txt += "<tr>" 
                            txt += "<td align=left style='padding-right: 3px;'> <b>mod:</b> </td>" 
                            txt += "<td align=left style='padding-right: 3px;'> %s - %s - %s </td>" % (hard_days, good_days, easy_days)
                            txt += "<td align=left style='padding-right: 3px;'> %s </td>" % (fmtTimeSpan(hard_days*86400, short=True))
                            txt += "<td align=left style='padding-right: 3px;'> %s </td>" % (fmtTimeSpan(good_days*86400, short=True))
                            txt += "<td align=left style='padding-right: 3px;'> %s </td>" % (fmtTimeSpan(easy_days*86400, short=True))
                            txt += "</tr>"

                            txt += "</table></p>"

            txt += "<hr>"
            txt += _("<h3>Current Card</h3>")

            if SHOW_DETAILLED_CARD_STATS_FOR_CURRENT_CARD:
                txt += d.cardStats(cc)
            else:
                txt += self.mini_card_stats(cc, True)
            txt += "<p>"
            txt += self._revlogData(cc, cs, NUM_OF_REVS)
        lc = r.lastCard()
        if lc:
            txt += "<hr>"
            txt += _("<h3>Last Card</h3>")
            if SHOW_DETAILLED_CARD_STATS_FOR_CURRENT_CARD:
                txt += d.cardStats(lc)
            else:
                txt += self.mini_card_stats(lc, False)
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
