# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


def get_menu(parent, menu_name):
    bar = parent.form.menubar
    for a in bar.actions():
        if menu_name == a.text():
            return a.menu()
    else:
        return bar.addMenu(menu_name)


def get_action(parent, action_name):
    bar = parent.form.menubar
    for a in bar.actions():
        if action_name == a.text():
            return a
    else:
        return bar.addAction(action_name)
