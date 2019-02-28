# -*- coding: utf-8 -*-

import time

import anki.stats as ankistats

from .config import local_conf
from .helper_functions import *



#copied from Browser, added IntDate column
#cleanup inspired by  warrior mode
def revlogData_mod(self, card, limit):
    entries = self.mw.col.db.all(
        "select id/1000.0, ease, ivl, factor, time/1000.0, type "
        "from revlog where cid = ?", card.id)
    if not entries:
        return ""

    list_of_rows = []
    
    row1 = [["Date","left"],
            ["T","right"],
            ["R","right"],
            ["Ivl","right"],
            ["IntDate","right"],
            ["Ease","right"],]
    if not local_conf.get('hide_time_column_from_revlog',False):
        row1.append(["Time","right"])
    list_of_rows.append(row1)

    limitentries = list(reversed(entries))[:limit]
    for (date, ease, ivl, factor, taken, type) in limitentries:
        tstr = [_("Lrn"), _("Rev"), _("ReLn"), _("Filt"), _("Resch")][type]
            #Learned, Review, Relearned, Filtered, Defered (Rescheduled)
        
        #COLORIZE LOG TYPE
        fmt = "<span style='color:%s'>%s</span>"
        if type == 0:
            tstr = fmt % (ankistats.colLearn, tstr)
        elif type == 1:
            tstr = fmt % (ankistats.colMature, tstr)
        elif type == 2:
            tstr = fmt % (ankistats.colRelearn, tstr)
        elif type == 3:
            tstr = fmt % ("#3c9690", tstr) # yellow  (ankistats.colCram, tstr)
        else:
            tstr = fmt % ("#000", tstr)

        #COLORIZE EASE
        if ease == 1:
            ease = fmt % (ankistats.colRelearn, ease)
        elif ease == 3:
            ease = fmt % ('navy', ease)
        elif ease == 4:
            ease = fmt % ('darkgreen', ease)

        int_due = "na"
        if ivl > 0:
            int_due_date = time.localtime(date + (ivl * 24 * 60 * 60))
            int_due = time.strftime(_("%Y-%m-%d"), int_due_date)

        ivl = formatIvlString(ivl)

        row_n = [[time.strftime("<b>%Y-%m-%d</b>@%H:%M",time.localtime(date)),"left"],
                    [tstr,"right"],
                    [ease,"right"],
                    [ivl,"right"],
                    [int_due,"right"],
                    [int(factor / 10) if factor else "","right"],]
        if not local_conf.get('hide_time_column_from_revlog',False):
            row_n.append([formatIvlString(taken),"right"])
        list_of_rows.append(list(row_n))  # copy list

    #show_info_length_of_sublists(list_of_rows)
    return  make_multi_column_table_first_row_bold(list_of_rows) 
