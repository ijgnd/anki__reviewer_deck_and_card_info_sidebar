from aqt import mw
from anki.utils import fmtTimeSpan

from .helper_functions import make_multi_column_table_first_row_bold


def v1(card, p):
    txt = ""
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

            row1 = [["", "left"],
                    ["days(h-g-e)", "left"],
                    ["hard(fmt)", "center"],
                    ["good(fmt)", "center"],
                    ["easy(fmt)", "center"],
                    ]
            row2 = [["<b>orig:</b>", "left"],
                    ["{} {} {}".format(orig_hard_days, orig_good_days, orig_easy_days), "left"],
                    [fmtTimeSpan(orig_hard_days*86400, short=True), "center"],
                    [fmtTimeSpan(orig_good_days*86400, short=True), "center"],
                    [fmtTimeSpan(orig_easy_days*86400, short=True), "center"],
                    ]
            row3 = [["<b>mod:</b>", "left"],
                    ["{} {} {}".format(hard_days, good_days, easy_days), "left"],
                    [fmtTimeSpan(hard_days*86400, short=True), "center"],
                    [fmtTimeSpan(good_days*86400, short=True), "center"],
                    [fmtTimeSpan(easy_days*86400, short=True), "center"],
                    ]

            # show_info_length_of_sublists([row1,row2,row3])
            return make_multi_column_table_first_row_bold([row1, row2, row3])


def v2(card, p):
    txt = ""
    fuzz = False
    try:
        orig_hard_days = mw.col.sched.original_nextRevIvl(card, 2, fuzz)
    except:
        return txt
    else:
        if orig_hard_days:
            orig_good_days = mw.col.sched.original_nextRevIvl(card, 3, fuzz)
            orig_easy_days = mw.col.sched.original_nextRevIvl(card, 4, fuzz)

            hard_days = mw.col.sched._nextRevIvl(card, 2, fuzz)
            good_days = mw.col.sched._nextRevIvl(card, 3, fuzz)
            easy_days = mw.col.sched._nextRevIvl(card, 4, fuzz)

            row1 = [["", "left"],
                    ["days(h-g-e)", "left"],
                    ["hard(fmt)", "center"],
                    ["good(fmt)", "center"],
                    ["easy(fmt)", "center"],
                    ]
            row2 = [["<b>orig:</b>", "left"],
                    ["{} {} {}".format(orig_hard_days, orig_good_days, orig_easy_days), "left"],
                    [fmtTimeSpan(orig_hard_days*86400, short=True), "center"],
                    [fmtTimeSpan(orig_good_days*86400, short=True), "center"],
                    [fmtTimeSpan(orig_easy_days*86400, short=True), "center"],
                    ]
            row3 = [["<b>mod:</b>", "left"],
                    ["{} {} {}".format(hard_days, good_days, easy_days), "left"],
                    [fmtTimeSpan(hard_days*86400, short=True), "center"],
                    [fmtTimeSpan(good_days*86400, short=True), "center"],
                    [fmtTimeSpan(easy_days*86400, short=True), "center"],
                    ]

            # show_info_length_of_sublists([row1,row2,row3])
            return make_multi_column_table_first_row_bold([row1, row2, row3])



def text_for_scheduler_comparison(card, p):
    if mw.col.sched.name == "std":
        return v1(card, p)
    if mw.col.sched.name == "std2":
        return v2(card, p)
