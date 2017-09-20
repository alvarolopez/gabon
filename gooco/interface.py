# Copyright 2017 Alvaro Lopez Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import curses

from gooco import contacts
from gooco import version


class Interface(object):
    def __init__(self):
        self.api = contacts.API
        self._contacts = None
        curses.wrapper(self.loop)

    @property
    def contacts(self):
        if self._contacts is None:
            # We assume that this is cached
            self._contacts = self.api.list_contacts()
        return self._contacts

    def draw_title(self):
        self.stdscr.addstr(0, 0, "gooco v" + version.version_string)
        self.stdscr.addstr(" | q: quit")
        self.stdscr.addstr("  h: help")
        self.stdscr.hline(1, 0, curses.ACS_HLINE, curses.COLS)
        self.stdscr.refresh()

    def draw_footer(self, last=None, all=None):
        self.stdscr.hline(curses.LINES - 1, 0, curses.ACS_HLINE, curses.COLS)
        if None not in (last, all):
            self.stdscr.addstr(curses.LINES - 1, 5, "(%s/%s)" % (last, all))
        self.stdscr.refresh()

    def show_help(self):
        self.content.clear()
        self.content.addstr(10, 30, "q")
        self.content.addstr(10, 50, "quit")
        self.content.addstr(11, 30, "h")
        self.content.addstr(11, 50, "show this help")

        self.content.addstr(13, 30, "arrows")
        self.content.addstr(13, 50, "scroll list")
        self.content.addstr(14, 30, "Page Down")
        self.content.addstr(14, 50, "Move to last item on screen")
        self.content.addstr(15, 30, "Page Up")
        self.content.addstr(15, 50, "Move to first item on screen")
        self.content.refresh()

    def loop(self, stdscr):
        self.stdscr = stdscr

        curses.curs_set(0)

        self.draw_title()
        self.draw_footer()

        self.content = curses.newwin(curses.LINES - 4, curses.COLS, 2, 0)

        self.content.addstr("Loading ...")
        self.content.refresh()

#        nr = self.add_contact_list(content)

        contact_list = ContactList(self.content, self.contacts)
        self.draw_footer(contact_list.end, len(self.contacts))

        while True:
            self.stdscr.refresh()
            k = self.stdscr.getkey()
            if k == "q":
                break
            elif k == "h":
                self.show_help()
            elif k == "KEY_PPAGE":
                contact_list.rw_one_page()
                self.draw_footer(contact_list.end,
                                 len(self.contacts))
            elif k == "KEY_NPAGE":
                contact_list.fw_one_page()
                self.draw_footer(contact_list.end,
                                 len(self.contacts))
            elif k == "KEY_DOWN":
                contact_list.fw_row()
                self.draw_footer(contact_list.end,
                                 len(self.contacts))
            elif k == "KEY_UP":
                contact_list.rw_row()
                self.draw_footer(contact_list.end,
                                 len(self.contacts))


class ContactList(object):
    def __init__(self, window, contacts):
        self.contacts = contacts
        self.window = window

        max_y, max_x = window.getmaxyx()
        self.max_rows = max_y - 1
        self.max_x = max_x - 1

        self.highlight = 1
        self.start = 0
        self.end = self.max_rows
        self.window.clear()
        self.window.addstr(0, 2, "Name", curses.A_BOLD)
        self.window.addstr(0, 42, "Email address", curses.A_BOLD)

        self.draw()

    def fw_row(self):
        if self.highlight == self.max_rows:
            if self.end < len(self.contacts):
                self.start += 1
                self.end = self.start + self.max_rows
        else:
            self.highlight += 1
        self.draw()

    def rw_row(self):
        if self.highlight == 1:
            if self.start > 0:
                self.start -= 1
                self.end -= 1
        else:
            self.highlight -= 1
        self.draw()

    def fw_one_page(self):
        if self.highlight == self.max_rows:
            # Advance one page
            if self.end + self.max_rows <= len(self.contacts):
                self.end += self.max_rows
                self.start = self.end - self.max_rows
            else:
                self.end = len(self.contacts)
                self.start = self.end - self.max_rows
        self.highlight = self.max_rows
        self.draw()

    def rw_one_page(self):
        if self.highlight == 1:
            if self.start - self.max_rows > 0:
                self.start = self.start - self.max_rows
                self.end = self.start + self.max_rows
            else:
                self.start = 0
                self.end = self.start + self.max_rows
        self.highlight = 1
        self.draw()

    def draw(self):
        for row, c in enumerate(self.contacts[self.start:], start=1):
            if row > self.max_rows:
                break
            if self.highlight == row:
                attr = curses.A_STANDOUT
            else:
                attr = 0
            self.window.addstr(row, 0, " " * self.max_x, attr)
            self.window.addstr(row, 2, c.name.encode('utf-8'), attr)
            self.window.addstr(row, 40, "  " + c.email, attr)
        self.window.refresh()
