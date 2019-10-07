#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyfiglet
import urwid
import time
import sys
import math

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]




class BannerHandler:

	def __init__(self, label):
		self.label = label
		#self.loop = loop

	def setup_view(self):
		#the full thing
		self.size_string = pyfiglet.figlet_format(self.label, font = "banner3-D",width=200)

		self.spacer = 0
		self.write_string = " "
		self.current_pos = 0
		#the width
		self.col_count = (len(self.size_string.partition('\n')[0]))

		#the depth
		self.line_count = self.size_string.count('\n')
		self.string_split = self.size_string.split('\n')
		x = self.string_split
		for line in x:
			self.write_string = self.write_string + (line[:self.current_pos] + "\n")  #use multipication to add more space here ex " " * 10
		self.current_pos = self.current_pos + 1
		self.lap = 0	
		
		self.view = urwid.Padding(urwid.Filler(urwid.Text(self.write_string,align='right'),'top'),'left')
		return self.view



        

	def refresh(self, loop):
		self.write_string = " "
		
		self.lapping = False
		x = self.string_split
		def spacer_calc():
			if self.current_pos > self.col_count and not((self.current_pos) >= loop):
				self.spacer = self.spacer + 1
			if (self.current_pos) >= loop:
				self.lap = self.lap + 1
				self.lapping = True
				self.spacer = self.spacer + 1
			if self.spacer == (loop):
				self.spacer = 0
			if self.lap == self.col_count:
				self.spacer = 0
				self.lap = 0
				self.current_pos = self.col_count

		spacer_calc()

		for line in x:
			if self.lapping == False:
				self.write_string = self.write_string + (line[:self.current_pos] + (" " * (self.spacer)) + "\n")  #use multipication to add more space here ex " " * 10
			else:
				self.write_string = self.write_string + right(line,self.col_count - self.lap) + (" " * ((self.spacer)-(self.lap))) + (line[:self.lap]) + "\n"
		#print(":" + self.write_string)
		self.current_pos = self.current_pos + 1
		self.view = urwid.Padding(urwid.Filler(urwid.Text(self.write_string,align='right'),'top'),'left')
		return self.view

class App:

	def setup_view(self):
		self.lookie = BannerHandler('uhh yeah dude')
		self.the_w = urwid.LineBox(self.lookie.setup_view(),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")


	def main(self):
		self.setup_view()
		self.loop = urwid.MainLoop(self.the_w, palette=[('body', 'dark cyan', '')])
		self.screen_size = self.loop.screen.get_cols_rows()[0] - 2
		self.loop.set_alarm_in(.2, self.refresh)
		self.loop.run()

	def refresh(self, loop=None, data=None):
		self.the_w = urwid.LineBox(self.lookie.refresh(self.screen_size),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
		self.loop.widget = self.the_w

		loop.set_alarm_in(.1, self.refresh)

if __name__ == "__main__":
	Please_work = App()
	sys.exit(Please_work.main())




		


