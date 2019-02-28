# -*- coding: utf-8 -*-

from .config import local_conf
from .helper_functions import *


mod_lower = local_conf.get('thresholds__ivl_mod_color__lower',70) 
mod_upper = local_conf.get('thresholds__ivl_mod_color__upper',110) 
lapse_lower = local_conf.get('thresholds__lapse_mod_color__lower',30)
lapse_upper = local_conf.get('thresholds__lapse_mod_color__upper',70)
im_colored = lambda p: fmt_int_as_str__maybe_in_critical_color(
    p.d_rev_IntMod_int,mod_lower,mod_upper)
lapse_colored = lambda p: fmt_int_as_str__maybe_in_critical_color(
    p.d_lapse_NewIvl_int,lapse_lower,lapse_upper)


def long_deck_options(card,p): 
    rows_long_deck_options = [
        ("Opt Group", p.d_OptionGroupName),             
        ("Learning Steps", p.d_new_steps_fmt[4:]),
        ("&nbsp;",'   ' +  p.d_new_steps_str),
        ("Graduating Ivl", p.d_new_GradIvl + ' days'),
        ("Easy Ivl", p.d_new_EasyIvl + ' days'),
        ("Easy Bonus", p.d_rev_easybonus + '%'),
        ("Ivl Mod", im_colored(p)),
        ("Lapse NewIvl", lapse_colored(p)),
        ]
    return make_two_column_table(rows_long_deck_options)


def text_for_short_options(card,p): 
    row1 = [["OptGr","left"],
            ["Steps","center"],
            ["LSteps","center"],
            ["GrIv","center"],
            ["EaIv","center"],
            ["EaBo","center"],
            ["IvMo","center"],
            ["LpIv","center"],]
    # option group names can be very long
    if len(p.d_OptionGroupName) > 15 and local_conf.get('deck_names_length',40):
        groupname = p.d_OptionGroupName_fmt
    else:
        groupname = p.d_OptionGroupName
    row2 = [[groupname,"left"],
            [p.d_new_steps_str[1:-1],"center"],
            [p.d_lapse_steps_str[1:-1],"center"],
            [p.d_new_GradIvl,"center"],
            [p.d_new_EasyIvl,"center"],
            [p.d_rev_easybonus,"center"],
            [im_colored(p),"center"],
            [lapse_colored(p),"center"],]
    #show_info_length_of_sublists([row1,row2])
    return make_multi_column_table_first_row_bold([row1,row2]) 
