from aqt import mw


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)
