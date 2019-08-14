#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyfiglet
import urwid
import time
import sys
import ast
import numpy

if __name__ == "__main__":
	full_size = pyfiglet.figlet_format('money', font = "isometric1")
	col_count = (len(full_size.partition('\n')[0]))
	line_count = full_size.count('\n')
	display_a = numpy.chararray((line_count,col_count))
	display_a[:] = " "
	x = full_size.split('\n')
	#print(display_a)
	#time.sleep(10)
	for line in x:
		print(line[:4] + (" " * 10) + "x")