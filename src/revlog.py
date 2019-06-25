import time

import anki.stats as ankistats
from anki.lang import _
from aqt import mw

from .config import gc
from .helper_functions import (
    formatIvlString,
    make_multi_column_table_first_row_bold
)


# copied from Browser, added IntDate column
# cleanup inspired by  warrior mode
def revlogData_mod(self, card, limit):
    entries = self.mw.col.db.all(
        "select id/1000.0, ease, ivl, factor, time/1000.0, type "
        "from revlog where cid = ?", card.id)
    if not entries:
        return ""

    list_of_rows = []
    
    row1 = [["Date", "left"],
            ["T", "right"],
            ["R", "right"],
            ["Ivl", "right"],
            ["IntDate", "right"],
            ["Ease", "right"],
            ]
    if not gc('hide_time_column_from_revlog', False):
        row1.append(["Time", "right"])
    list_of_rows.append(row1)

    limitentries = list(reversed(entries))[:limit]
    for (date, ease, ivl, factor, taken, type) in limitentries:
        tstr = [_("Lrn"), _("Rev"), _("ReLn"), _("Filt"), _("Resch")][type]
            # Learned, Review, Relearned, Filtered, Defered (Rescheduled)
        
        # COLORIZE LOG TYPE
        fmt = "<span class='%s'>%s</span>"
        if type == 0:
            tstr = fmt % ("color_learn", tstr)
        elif type == 1:
            tstr = fmt % ("color_mature", tstr)
        elif type == 2:
            tstr = fmt % ("color_relearn", tstr)
        elif type == 3:
            tstr = fmt % ("color_type3", tstr) # yellow  (ankistats.colCram, tstr)
        else:
            tstr = fmt % ("color_rest", tstr)

        #COLORIZE EASE
        if ease == 1:
            ease = fmt % ("color_relearn", ease)
        elif ease == 3:
            ease = fmt % ("color_ease3", ease)
        elif ease == 4:
            ease = fmt % ("color_ease4", ease)

        int_due = "na"
        if ivl > 0:
            int_due_date = time.localtime(date + (ivl * 24 * 60 * 60))
            int_due = time.strftime(_("%Y-%m-%d"), int_due_date)

        ivl = formatIvlString(ivl)

        row_n = [[time.strftime("<b>%Y-%m-%d</b>@%H:%M", time.localtime(date)), "left"],
                    [tstr, "right"],
                    [ease, "right"],
                    [ivl, "right"],
                    [int_due, "right"],
                    [int(factor / 10) if factor else "", "right"],
                    ]
        if not gc('hide_time_column_from_revlog', False):
            row_n.append([formatIvlString(taken), "right"])
        list_of_rows.append(list(row_n))  # copy list

    # show_info_length_of_sublists(list_of_rows)
    return  make_multi_column_table_first_row_bold(list_of_rows) 
