import os
import io
import time
from collections import OrderedDict

from aqt import mw
from anki.utils import fmtTimeSpan
from aqt.utils import showInfo

from .config import gc


# about due_day
# this code is used in anki.stats.report() that is called
# by the Extended Browser/Browser - info
# to calculate a due column
# if c.type in (1,2):
#     if c.odid or c.queue < 0:
#         next = None
#     else:
#         if c.queue in (2,3):
#             next = time.time()+((c.due - self.col.sched.today)*86400)
#         else:
#             next = c.due
#         next = self.date(next)
#     if next:
#         self.addLine(_("Due"), next)


def due_day(card):
    if card.queue <= 0:
        return ""
    else:
        if card.queue in (2, 3):
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


def valueForOverdue(card):
    # warrior mode only uses:
    return mw.col.sched._daysLate(card)

    # shorter version of code rom below
    # if card.queue == 2:
    #     return mw.col.sched._daysLate(card)
    # else:
    #     return ""

    # Advanced Browser has overdue_days in  custom_fields.py : Advantage ??
    # if card.queue == 0 or card.queue == 1 or card.type == 0:
    #     myvalue = 0
    # elif card.odue and (card.queue in (2,3) or (type == 2 and card.queue < 0)):
    #     myvalue = card.odue
    # elif card.queue in (2,3) or (card.type == 2 and card.queue < 0):
    #     myvalue = card.due
    # if myvalue:
    #     diff = myvalue - mw.col.sched.today
    #     if diff < 0:
    #         return diff * -1
    #     else:
    #         return ""
    # else:
    #     return ""


def percent_overdue(card):
    overdue = mw.col.sched._daysLate(card)
    ivl = card.ivl
    if card.ivl > 0:
        return (overdue+ivl)/ivl


def fmt_long_string(name, value):
    l = 0
    u = value
    out = ""
    while l < len(name):
        out += name[l:l+u] + '\n'
        l += u
    return out.rstrip('\n')


def fmt_int_as_str__maybe_in_critical_color(valueInt, lower, upper):
    if gc('highlight_colors', False):
        if valueInt <= lower:
            return "<div class='critical_color_lower'>{}</div>".format(str(valueInt))
        elif valueInt >= upper:
            return "<div class='critical_color_upper'>{}</div>".format(str(valueInt))
    else:
        return str(valueInt)


def make_two_column_table(d):
    o = OrderedDict(d)
    txt = ""
    txt += "<p> <table width=100%>"
    for k, v in o.items():  # makeLine from stats.py adjusted
        txt += "<tr><td align=left width='35%' style='padding-right: 3px;'>"
        txt += "<b>%s</b></td><td>%s</td></tr>" % (k, v)
    txt += "</table></p>"
    return txt


def make_multi_column_table(rowlist):
    """takes a list of lists. Each sublist must have four entries: Value - htmlcode before value -
    htmlcode after value - alignment. I think having the value first is more clear"""
    txt = "<p> <table width=100%>"
    for r in rowlist:
        txt += "<tr>"
        for c in r:
            txt += "<td align='%s' style='padding-right: 3px;'> %s %s %s</td>" % (
                c[3], c[1], str(c[0]), c[2])
        txt += "</tr>"
    txt += "</table></p>"
    return txt


def make_multi_column_table_first_row_bold(rowlist):
    """takes a list of lists. Each sublist must have two entries: Value - alignment """
    for i, r in enumerate(rowlist):
        for c in r:
            if i == 0:
                c.insert(1, "<b>")
                c.insert(2, "</b>")
            else:
                c.insert(1, "")
                c.insert(2, "")
    return make_multi_column_table(rowlist)


def deck_name_and_source_for_filtered(card, p):
    max_length = gc('deck_names_length', 0)
    rows = []
    if len(p.deckname) > max_length:
        rows.append(("Deck:", p.deckname_fmt))
    else:
        rows.append(("Deck:", p.deckname))
    if card.odid:
        if len(p.source_deck_name) > max_length:
            rows.append(("Source Deck", p.source_deck_name_fmt))
        else:
            rows.append(("Source Deck", p.source_deck_name))
    return make_two_column_table(rows)


# function time from anki/stats.py
def stattime(tm):
    str = ""
    if tm >= 60:
        str = fmtTimeSpan((tm / 60)*60, short=True, point=-1, unit=1)
    if tm % 60 != 0 or not str:
        str += fmtTimeSpan(tm % 60, point=2 if not str else -1, short=True)
    return str


# from warrior-mode
def formatIvlString(ivl):
    if ivl == 0:
        return "0d"
    elif ivl > 0:
        return fmtTimeSpan(ivl * 86400, short=True)
    else:
        return stattime(-ivl)


# for debugging
def show_info_length_of_sublists(lol):
    mystr = ""
    def sublist_length(s):
        out = ""
        for e in s:
            out += str(len(e)) + ' '
        return out
    for l in lol:
        mystr += sublist_length(l) + ' '
    showInfo(mystr)


def sidebar_style(file):
    addon_path = os.path.dirname(__file__)
    csspath = os.path.join(addon_path, file)
    with io.open(csspath, encoding="utf-8") as f:
        mystyle = f.read()
    return mystyle + " td { font-size: 80%; }"
