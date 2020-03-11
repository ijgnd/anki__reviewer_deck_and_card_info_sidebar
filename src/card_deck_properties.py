import time
from types import SimpleNamespace

from aqt import mw
from anki.utils import fmtTimeSpan

from .helper_functions import due_day, stattime, valueForOverdue, percent_overdue, fmt_long_string
from .config import gc


def current_card_deck_properties(card):
    if card.odid:
        conf = mw.col.decks.confForDid(card.odid)
        source_deck_name = mw.col.decks.get(card.odid)['name']
    else:
        conf = mw.col.decks.confForDid(card.did)
        source_deck_name = ""

    formatted_steps = ''
    for i in conf['new']['delays']:
        formatted_steps += ' -- ' + fmtTimeSpan(i * 60, short=True)

    #############
    # from anki.stats.py
    (cnt, total) = mw.col.db.first(
            "select count(), sum(time)/1000 from revlog where cid = :id",
            id=card.id)
    first = mw.col.db.scalar(
        "select min(id) from revlog where cid = ?", card.id)
    last = mw.col.db.scalar(
        "select max(id) from revlog where cid = ?", card.id)

    def date(tm):
        return time.strftime("%Y-%m-%d", time.localtime(tm))

    p = dict()
    # Card Stats as seen in Browser
    p["c_Added"] = date(card.id/1000)
    p["c_FirstReview"] = date(first/1000) if first else ""
    p["c_LatestReview"] = date(last/1000) if last else ""
    p["c_Due"] = due_day(card)
    p["c_Interval"] = fmtTimeSpan(card.ivl * 86400, short=True) if card.queue == 2 else ""
    p["c_Ease"] = "%d%%" % (card.factor/10.0)
    p["c_Ease_str"] = str("%d%%" % (card.factor/10.0))
    p["c_Reviews"] = "%d" % card.reps
    p["c_Lapses"] = "%d" % card.lapses
    p["c_AverageTime"] = stattime(total / float(cnt)) if cnt else ""
    p["c_TotalTime"] = stattime(total) if cnt else ""
    p["c_Position"] = card.due if card.queue == 0 else ""
    p["c_CardType"] = card.template()['name']
    p["c_NoteType"] = card.model()['name']
    p["c_Deck"] = mw.col.decks.name(card.did)
    p["c_NoteID"] = card.nid
    p["c_CardID"] = card.id
    p["c_did"] = card.did
    p["c_ord"] = card.ord

    # other useful info
    p["cnt"] = cnt
    p["total"] = total
    p["card_ivl_str"] = str(card.ivl)
    p["dueday"] = str(due_day(card))
    p["value_for_overdue"] = str(valueForOverdue(card))
    p["overdue_percent"] = str(percent_overdue(card))
    p["actual_ivl"] = str(card.ivl + valueForOverdue(card))
    p["c_type"] = card.type
    p["deckname"] = mw.col.decks.get(card.did)['name']
    p["deckname_fmt"] = fmt_long_string(
        mw.col.decks.get(card.did)['name'], gc('deck_names_length', 40))
    p["source_deck_name"] = source_deck_name
    p["source_deck_name_fmt"] = fmt_long_string(source_deck_name, gc('deck_names_length', 40))
    p["now"] = time.strftime('%Y-%m-%d %H:%M', time.localtime(card.id/1000))
    p["conf"] = conf
    # Deck Options
    p["d_OptionGroupID"] = conf['id']
    p["d_OptionGroupName"] = conf['name']
    p["d_OptionGroupName_fmt"] = fmt_long_string(conf['name'], gc('optiongroup_names_length', 20))
    p["d_IgnoreAnsTimesLonger"] = conf["maxTaken"]
    p["d_ShowAnswerTimer"] = conf["timer"]
    p["d_Autoplay"] = conf["autoplay"]
    p["d_Replayq"] = conf["replayq"]
    p["d_IsDyn"] = conf["dyn"]
    p["d_usn"] = conf["usn"]
    p["d_mod"] = conf["mod"]
    p["d_new_steps"] = conf['new']['delays']
    p["d_new_steps_str"] = str(conf['new']['delays'])
    p["d_new_steps_fmt"] = formatted_steps
    p["d_new_order"] = conf['new']['order']
    p["d_new_NewPerDay"] = conf['new']['perDay']
    p["d_new_GradIvl"] = str(conf['new']['ints'][0])
    p["d_new_EasyIvl"] = str(conf['new']['ints'][1])
    p["d_new_StartingEase"] = conf['new']['initialFactor'] / 10
    p["d_new_BurySiblings"] = conf['new']['bury']
    p["d_new_sep"] = conf['new']["separate"]  # unused
    p["d_rev_perDay"] = conf['rev']['perDay']
    p["d_rev_easybonus"] = str(int(100 * conf['rev']['ease4']))
    p["d_rev_IntMod_int"] = int(100 * conf['rev']['ivlFct'])
    p["d_rev_IntMod_str"] = str(int(100 * conf['rev']['ivlFct']))
    p["d_rev_MaxIvl"] = conf['rev']['maxIvl']
    p["d_rev_BurySiblings"] = conf['rev']['bury']
    p["d_rev_minSpace"] = conf['rev']["minSpace"]  # unused
    p["d_rev_fuzz"] = conf['rev']["fuzz"]     # unused
    p["d_lapse_steps"] = conf['lapse']['delays']
    p["d_lapse_steps_str"] = str(conf['lapse']['delays'])
    p["d_lapse_NewIvl_int"] = int(100 * conf['lapse']['mult'])
    p["d_lapse_NewIvl_str"] = str(int(100 * conf['lapse']['mult']))
    p["d_lapse_MinInt"] = conf['lapse']['minInt']
    p["d_lapse_LeechThresh"] = conf['lapse']['leechFails']
    p["d_lapse_LeechAction"] = conf['lapse']['leechAction']
    return SimpleNamespace(**p)
