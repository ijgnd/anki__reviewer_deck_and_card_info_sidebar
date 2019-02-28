# -*- coding: utf-8 -*-

import time
from collections import namedtuple

from aqt import mw
from anki.utils import fmtTimeSpan

from .config import local_conf
from .helper_functions import *

def current_card_deck_properties_as_namedtuple(card):
    p = namedtuple('CardProps', """
            c_Added
            c_FirstReview
            c_LatestReview
            c_Due
            c_Interval
            c_Ease
            c_Ease_str
            c_Reviews
            c_Lapses
            c_AverageTime
            c_TotalTime
            c_Position
            c_CardType
            c_NoteType
            c_Deck
            c_NoteID
            c_CardID

            cnt
            total
            card_ivl_str
            dueday
            value_for_overdue
            actual_ivl
            c_type
            deckname
            deckname_fmt
            source_deck_name
            source_deck_name_fmt
            now
            
            conf
            
            d_OptionGroupID
            d_OptionGroupName
            d_OptionGroupName_fmt
            d_IgnoreAnsTimesLonger
            d_ShowAnswerTimer
            d_Autoplay
            d_Replayq
            d_IsDyn
            d_usn
            d_mod
            d_new_steps
            d_new_steps_str
            d_new_steps_fmt
            d_new_order
            d_new_NewPerDay
            d_new_GradIvl
            d_new_EasyIvl
            d_new_StartingEase
            d_new_BurySiblings
            d_new_sep
            d_rev_perDay
            d_rev_easybonus
            d_rev_IntMod_int
            d_rev_IntMod_str
            d_rev_MaxIvl
            d_rev_BurySiblings
            d_rev_minSpace
            d_rev_fuzz
            d_lapse_steps
            d_lapse_steps_str
            d_lapse_NewIvl_int
            d_lapse_NewIvl_str
            d_lapse_MinInt
            d_lapse_LeechThresh
            d_lapse_LeechAction
            """)


    if card.odid:
        conf=mw.col.decks.confForDid(card.odid)
        source_deck_name = mw.col.decks.get(card.odid)['name']
    else:
        conf=mw.col.decks.confForDid(card.did)
        source_deck_name=""

    formatted_steps = ''
    for i in conf['new']['delays']:
        formatted_steps += ' -- ' + fmtTimeSpan(i * 60, short=True)
    
    #############
    #from anki.stats.py
    (cnt, total) = mw.col.db.first(
            "select count(), sum(time)/1000 from revlog where cid = :id",
            id=card.id)
    first = mw.col.db.scalar(
        "select min(id) from revlog where cid = ?", card.id)
    last = mw.col.db.scalar(
        "select max(id) from revlog where cid = ?", card.id)

    def date(tm):
        return time.strftime("%Y-%m-%d", time.localtime(tm))

    fmt = lambda x, **kwargs: fmtTimeSpan(x, short=True, **kwargs)


    out = p(
            #Card Stats as seen in Browser
            c_Added        = date(card.id/1000),
            c_FirstReview  = date(first/1000) if first else "",
            c_LatestReview = date(last/1000)if last else "",
            c_Due          = due_day(card),
            c_Interval     = fmt(card.ivl * 86400) if card.queue == 2 else "",
            c_Ease         ="%d%%" % (card.factor/10.0),
            c_Ease_str     = str("%d%%" % (card.factor/10.0)),
            c_Reviews      = "%d" % card.reps,
            c_Lapses       = "%d" % card.lapses,
            c_AverageTime  = stattime(total / float(cnt)) if cnt else "",
            c_TotalTime    = stattime(total) if cnt else "",
            c_Position     = card.due if card.queue == 0 else "",
            c_CardType     = card.template()['name'],
            c_NoteType     = card.model()['name'],
            c_Deck         = mw.col.decks.name(card.did),
            c_NoteID       = card.nid,
            c_CardID       = card.id,

            #other useful info
            cnt=cnt,
            total=total,
            card_ivl_str=str(card.ivl),
            dueday=str(due_day(card)),
            value_for_overdue=str(valueForOverdue(card)),
            actual_ivl= str(card.ivl + valueForOverdue(card)),
            c_type=card.type,
            deckname=mw.col.decks.get(card.did)['name'],
            deckname_fmt=fmt_long_string(mw.col.decks.get(card.did)['name'],local_conf.get('deck_names_length',40)),
            source_deck_name=source_deck_name,
            source_deck_name_fmt=fmt_long_string(source_deck_name,local_conf.get('deck_names_length',40)),
            now = time.strftime('%Y-%m-%d %H:%M', time.localtime(card.id/1000)),
            
            conf = conf,
            #Deck Options
            d_OptionGroupID       = conf['id'],
            d_OptionGroupName     = conf['name'],
            d_OptionGroupName_fmt = fmt_long_string(conf['name'],local_conf.get('optiongroup_names_length',20)),
            d_IgnoreAnsTimesLonger= conf["maxTaken"],
            d_ShowAnswerTimer     = conf["timer"],
            d_Autoplay            = conf["autoplay"],
            d_Replayq             = conf["replayq"],
            d_IsDyn               = conf["dyn"],
            d_usn                 = conf["usn"],
            d_mod                 = conf["mod"],
            d_new_steps           = conf['new']['delays'],
            d_new_steps_str       = str(conf['new']['delays']),
            d_new_steps_fmt       = formatted_steps,
            d_new_order           = conf['new']['order'],
            d_new_NewPerDay       = conf['new']['perDay'],
            d_new_GradIvl         = str(conf['new']['ints'][0]), 
            d_new_EasyIvl         = str(conf['new']['ints'][1]),
            d_new_StartingEase    = conf['new']['initialFactor'] / 10 ,
            d_new_BurySiblings    = conf['new']['bury'],
            d_new_sep             = conf['new']["separate"], #unused
            d_rev_perDay          = conf['rev']['perDay'],
            d_rev_easybonus       = str(int(100 * conf['rev']['ease4'])),
            d_rev_IntMod_int      = int(100 * conf['rev']['ivlFct']),     
            d_rev_IntMod_str      = str(int(100 * conf['rev']['ivlFct'])),          
            d_rev_MaxIvl          = conf['rev']['maxIvl'],
            d_rev_BurySiblings    = conf['rev']['bury'],
            d_rev_minSpace        = conf['rev']["minSpace"], # unused
            d_rev_fuzz            = conf['rev']["fuzz"],     # unused
            d_lapse_steps         = conf['lapse']['delays'],
            d_lapse_steps_str     = str(conf['lapse']['delays']),
            d_lapse_NewIvl_int    = int(100 * conf['lapse']['mult']),
            d_lapse_NewIvl_str    = str(int(100 * conf['lapse']['mult'])),
            d_lapse_MinInt        = conf['lapse']['minInt'],
            d_lapse_LeechThresh   = conf['lapse']['leechFails'],
            d_lapse_LeechAction   = conf['lapse']['leechAction'],
    )
    return out 
