#!/usr/bin/env python
# -*- coding: utf-8 -*-
from colored import fg, bg, attr
import pyfiglet
import urwid
import time

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

class Banner(urwid.WidgetWrap):
	
	def __init__(self, label):
		self.const_text = label
		self.current_text = left(label,1)
		self.roller = 1
		self.banner_t = pyfiglet.figlet_format(self.current_text, font = "slant")
		self.banner_w = urwid.Text(self.banner_t)

	def figamate(self):
		self.roller = self.roller + 1
		self.current_text = left(label, roller)

	def fig_start():
		return self.banner_w





if __name__ == "__main__":
	banner_w = Banner('money')
	banner_final = urwid.Padding(urwid.Filler(banner_w.fig_start,'top'),'center')
	loop = urwid.MainLoop(banner_final).run()
	#loop.set_alarm_in(1,banner_w.figamate)

