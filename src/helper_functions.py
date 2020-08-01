import os
import io
import time
from collections import OrderedDict

from aqt import mw
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
    # return mw.col.sched._daysLate(card)
    # doesn't work in filtered deck for me for a card with these properties

    # pp(card) for card I recently failed from filtered deck (I removed irrelevant parts)
    # {'data': '', 'did': 000, 'due': 1582139003, 'factor': 2450, 'flags': 0, 'id': 00, 'ivl': 2, 
    #  'lapses': 1, 'left': 1001, 'mod': 00, 'nid': 000, 'odid': 01, 'odue': 0, 'ord': 0, 
    #  'queue': 1, 'reps': 3, 'type': 3, 'usn': -1}

    # Advanced Browser has overdue_days in  custom_fields.py : Advantage ??
    # https://github.com/hssm/advanced-browser/blob/9ffa602171a94e5e06ece9e5959c5ed3f74c0241/advancedbrowser/advancedbrowser/custom_fields.py#L225
    # not good either because cards in filtered decks can be overdue, too
        # def valueForOverdue(self, odid, queue, type, due):
        # if odid or queue == 1:
        #     return
        # elif queue == 0 or type == 0:
        #     return
        # elif queue in (2,3) or (type == 2 and queue < 0):
        #     diff = due - mw.col.sched.today
        #     if diff < 0:
        #         return diff * -1
        #     else:
        #         return

    if card.queue in (0,1) or card.type == 0:
        myvalue = 0
    elif card.odue and (card.queue in (2,3) or (type == 2 and card.queue < 0)):
        myvalue = card.odue
    elif card.queue in (2,3) or (card.type == 2 and card.queue < 0):
        myvalue = card.due
    if myvalue:
        diff = myvalue - mw.col.sched.today
        if diff < 0:
            a = diff * - 1
            return max(0, a)
        else:
            return 0
    else:
        return 0


def percent_overdue(card):
    overdue = valueForOverdue(card)
    ivl = card.ivl
    if ivl > 0:
        return "{0:.2f}".format((overdue+ivl)/ivl*100)
    else:
        return "0"


def fmt_long_string(name, value):
    l = 0
    u = value
    out = ""
    while l < len(name):
        out += name[l:l+u] + '\n'
        l += u
    return out.rstrip('\n')


def fmt_as_str__maybe_in_critical_color(value, lower, upper, usespan=False, invert=False):
    valueInt = int(value)
    valueStr = str(value)
    tag = "span" if usespan else "div"
    lowclass = "critical_color_upper" if invert else "critical_color_lower"
    highclass = "critical_color_lower" if invert else "critical_color_upper"
    if gc('highlight_colors', False):
        if valueInt <= lower:
            return f"<{tag} class='{lowclass}'>{valueStr}</{tag}>"
        elif valueInt >= upper:
            return f"<{tag} class='{highclass}'>{valueStr}</{tag}>"
        else:
            return valueStr
    else:
        return valueStr


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
