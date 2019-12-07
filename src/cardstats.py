from aqt import mw

from .config import gc
from .helper_functions import make_two_column_table


def mini_card_stats(card, p, showOD):
    """mini_card_stats is called for current and prior card. Overdue days doesn't make sense
    for recently rated cards. So there needs to be an option to hide it. """
    # originally this was:
    # card_ivl_str=str(card.ivl),
    # dueday=str(self.due_day(card)),
    # value_for_overdue=str(self.valueForOverdue(card)),
    # actual_ivl
    right_column = p.card_ivl_str + ' (scheduled)'
    clickable_cid = '''<a href=# onclick="return pycmd('%s')">%s</a>''' %(
        "BrowserSearch#" + str(p.c_CardID), str(p.c_CardID))
    rows_mini_stats = [
        ("Ivl", right_column),
        # ("sched Ivl",p.card_ivl_str),
        # ("actual Ivl",p.card_ivl_str),
        ("Due day", p.dueday),
        ("cid/card created", clickable_cid + '&nbsp;&nbsp;--&nbsp;&nbsp;' + p.now),
        ("Ease", p.c_Ease_str),
    ]
    if showOD:
        rows_mini_stats.insert(1, ("Overdue days: ", p.value_for_overdue + '  (' + p.overdue_percent + '%)' ))
    return make_two_column_table(rows_mini_stats)
    return make_two_column_table(rows_mini_stats)


def card_stats_as_in_browser(card, p):
    # Extended Card Stats shows the info field that you see when you
    # click "Info" in the toolbar of the browser with this line:
    txt = ""
    # txt = self.mw.col.cardStats(card)
    # I rebuild this option here, so that it's easier to customize.
    as_in_browser = [
        ("Added", p.c_Added),
        ("First Review", p.c_FirstReview),
        ("Latest Review", p.c_LatestReview),
        ("Due", p.c_Due),
        ("Interval", p.c_Interval),
        ("Ease", p.c_Ease_str),
        ("Reviews", p.c_Reviews),
        ("Lapses", p.c_Lapses),
        ("Card Type", p.c_CardType),
        ("Note Type", p.c_NoteType),
        ("Deck", p.c_Deck),
        ("Note ID", p.c_NoteID),
        ("Card ID", p.c_CardID),
        ]
    if p.cnt:
        as_in_browser.insert(7, ("Average Time", p.c_AverageTime))
        as_in_browser.insert(8, ("Total Time", p.c_TotalTime))
    return txt + make_two_column_table(as_in_browser)
