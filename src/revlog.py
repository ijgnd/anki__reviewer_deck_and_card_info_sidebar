import time

from anki.rsbackend import FormatTimeSpanContext

from .config import gc
from .helper_functions import (
    make_multi_column_table_first_row_bold,
    timespan,
)


# copied from Browser, added IntDate column
# cleanup inspired by  warrior mode
def revlog_data_mod(self, card, limit):
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
            # ["dueDate", "right"],
            ["Ease", "right"],
            ]
    if not gc('hide_time_column_from_revlog', False):
        row1.append(["Time", "right"])
    list_of_rows.append(row1)

    limitentries = list(reversed(entries))[:limit]
    for (date, ease, ivl, factor, taken, _type) in limitentries:
        tstr = ["Lrn", "Rev", "ReLn", "Filt", "Resch"][_type]
            # Learned, Review, Relearned, Filtered, Defered (Rescheduled)  # noqa
        
        # COLORIZE LOG TYPE
        fmt = "<span class='%s'>%s</span>"
        if type == 0:
            tstr = fmt % ("color_learn", tstr)
        elif type == 1:
            tstr = fmt % ("color_mature", tstr)
        elif type == 2:
            tstr = fmt % ("color_relearn", tstr)
        elif type == 3:
            tstr = fmt % ("color_type3", tstr)  # yellow  (ankistats.colCram, tstr)
        else:
            tstr = fmt % ("color_rest", tstr)

        # COLORIZE EASE
        if ease == 1:
            ease = fmt % ("color_relearn", ease)
        elif ease == 3:
            ease = fmt % ("color_ease3", ease)
        elif ease == 4:
            ease = fmt % ("color_ease4", ease)

        int_due = "na"  # noqa

        if ivl > 0:
            int_due_date = time.localtime(date + (ivl * 24 * 60 * 60))  # noqa
            int_due = time.strftime("%Y-%m-%d", int_due_date)  # noqa

        # https://github.com/ankitects/anki/blob/394f7c630cd8b951d17171030c0859e092c03d41/qt/aqt/browser.py#L1489
        if ivl == 0:
            ivl = ""
        else:
            if ivl > 0:
                ivl *= 86_400
            # cs = ankistats.CardStats(self.mw.col, card)
            # ivl = cs.time(abs(ivl))
            #     def time(self, tm: float) -> str:
            #         return self.col.backend.format_time_span(
            #             tm, context=FormatTimeSpanContext.PRECISE
            #         )
            
            # PRECISE: 1.23 months vs. ANSWER_BUTTONS ⁨1.2⁩mo
            context = FormatTimeSpanContext.ANSWER_BUTTONS  # PRECISE
            ivl = timespan(abs(ivl), context=context)

        row_n = [[time.strftime("<b>%Y-%m-%d</b>@%H:%M", time.localtime(date)), "left"],
                 [tstr, "right"],
                 [ease, "right"],
                 [ivl, "right"],
                 # [int_due, "right"],
                 [int(factor / 10) if factor else "", "right"],
                 ]
        if not gc('hide_time_column_from_revlog', False):
            row_n.append([timespan(taken), "right"])
        list_of_rows.append(list(row_n))  # copy list

    # show_info_length_of_sublists(list_of_rows)
    return make_multi_column_table_first_row_bold(list_of_rows)
