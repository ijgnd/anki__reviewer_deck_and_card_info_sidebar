# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.webview import AnkiWebView

from .sidebar_set_contents import update_contents_of_sidebar


class StatsSidebar(object):
    def __init__(self, mw):
        self.mw = mw
        self.shown = False
        addHook("showQuestion", self._update_contents_of_sidebar)
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)


    def _addDockable(self, title, w):
        class DockableWithClose(QDockWidget):
            closed = pyqtSignal()
            def closeEvent(self, evt):
                self.closed.emit()
                QDockWidget.closeEvent(self, evt)
        dock = DockableWithClose(title, mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable)
        dock.setWidget(w)
        if mw.width() < 600:
            mw.resize(QSize(600, mw.height()))
        mw.addDockWidget(Qt.RightDockWidgetArea, dock)
        return dock


    def _remDockable(self, dock):
        mw.removeDockWidget(dock)


    def show(self):
        if not self.shown:
            class ThinAnkiWebView(AnkiWebView):
                def sizeHint(self):
                    return QSize(200, 100)
            self.web = ThinAnkiWebView()
            self.shown = self._addDockable("Card Info", self.web)
            self.shown.closed.connect(self._onClosed)

        self._update_contents_of_sidebar()


    def hide(self):
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None
            #actionself.mw.form.actionCstats.setChecked(False)


    def toggle(self):
        if self.shown:
            self.hide()
        else:
            self.show()


    def _onClosed(self):
        # schedule removal for after evt has finished
        self.mw.progress.timer(100, self.hide, False)


    def _update_contents_of_sidebar(self):
        update_contents_of_sidebar(self)

