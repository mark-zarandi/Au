#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urwid
import time
import sys
import hjson
import json
import numpy
from ansi_alphabet import the_alphabet
import requests

blank_column = [[0],[0],[0],[0],[0]]
def line_split(input_string):
    string = (input_string.lower().split())
    if len(string) == 1 and len(string[0]) <= 7:
        return (str(string[0]))
    if len(string[0]+string[1]) > 7 and len(string[0])<=7:
        return (string[0] + "_" + string[1])
    if len(string[0]+string[1]) <= 7 and len(string)<3:
        return(string[0]+string[1])
    if len(string[0]+string[1]) <= 7 and len(string) >= 3:
        return(string[0]+string[1]+"_"+string[2])

class BoxButton(urwid.WidgetWrap):
   
    def __init__(self, label, place_int=-1, on_press=None, user_data=None):
        _top_char = u'\u2580'
        _top_corner = u'\u2584'
        _bottom_char = u'\u2584'
        _bottom_corner = u'\u2580'
        padding_size = 2
        #move border calcs further down.
        x = line_split(label).split("_")
        lookie = lambda t: len(t)
        vfunc = numpy.vectorize(lookie)

        top_border = _top_corner + (_top_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)) + _top_corner
        bottom_border = _bottom_corner + (_bottom_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)) + _bottom_corner
        cursor_position = len(top_border)
        self.label = label
      
        ansi_word = []

        
        def label_construct(one_liner):
            
            label_break = one_liner.split("_")
            full_label =[]
            first_token = True
            for token in label_break:

                return_word = []
                first = True
                for letter_work in token:
                    if first:
                        return_word.append(the_alphabet[letter_work])
                        first = False
                    else:
                        #return_word.append(blank_column)
                        return_word.append(the_alphabet[letter_work])
                    return_word.append(blank_column)

                word_joined = numpy.concatenate(return_word, 1)
                full_label.append(word_joined)
            if len(label_break) > 1:
                if full_label[0].shape != full_label[1].shape:
                    full_label = find_and_fill(full_label)
                blank_line = numpy.zeros((1,int(len(full_label[0][0]))))
                full_label[0] = numpy.insert(full_label[0],len(full_label[0]),[blank_line],axis=0)
                    
                return numpy.concatenate(full_label,0)
            else:
                return word_joined

        def find_and_fill(to_fill):
            shape_size = (to_fill[1].shape)

            largest_index = -1
            #add filler on smallest
            size_list = numpy.zeros((3,len(to_fill)))
            for x in to_fill:
                
                size_list[0][to_fill.index(x)] = int(to_fill.index(x))
                size_list[1][to_fill.index(x)] = len(x[1])


            
            big = max(size_list[1])
            shape_size = int(min(size_list[1]))
            for x in to_fill:
                if big - len(x[1]) != 0:
                    size_list[2][to_fill.index(x)] = int(big - len(x[1]))

                    loop_counter = int(size_list[2][to_fill.index(x)])
                    #select line
                    go_here = int(size_list[0][to_fill.index(x)])
                    #split left and right going forward.
                    left = int(round(loop_counter/2,0))
                    right = int(loop_counter-left)
                    #right is easiest
                    for y in range(right):
                        to_fill[go_here] = numpy.insert(to_fill[go_here],shape_size+y,0,axis=1)
                    #left
                    for y in range(left):
                        to_fill[go_here] = numpy.insert(to_fill[go_here],y-1,0,axis=1)
            
            return to_fill

           
        word_array = label_construct(line_split(label))

        new_line = ''
        ansi_word.append(urwid.Text(top_border,align='center'))

        for x in word_array:
            new_line = ""
            new_line = u'\u2588' + u'\u0020' + u'\u0020'
            for y in x:
                #1 Full Block
                #2 Half Top Block
                #0 Space
                #3 Half Bottom Block
                #4 right half block
                #5 right 1/8th 
                #6 right 7/8
                #12 left half block
                #11 left 7/8 block
                #10 left 1/8 block
                #15 lower one quarter
                #16 Left 

                switcher = {
                1:u"\u2588",
                0:u"\u0020",
                2:u"\u2580",
                3:u"\u2584",
                4:u"\u2590",
                5:u"\u2595",
                6:u"\u259B",
                11:u"\u2589",
                10:u"\u258F",
                15:u"\u2582",
                12:u"\u258C"
                }
                new_line = new_line + switcher.get(y)
            new_line = new_line + u'\u0020' + u'\u2588'# + u"\n"
            ansi_word.append(urwid.Text(new_line,align="center"))
        ansi_word.append(urwid.Text(bottom_border,align='center'))
        self.widget = urwid.Pile(ansi_word)
        self._hidden_btn = urwid.Button('hidden %s' % label + str(place_int), on_press, user_data)

        super(BoxButton, self).__init__(self.widget)
    def get_label_p(self):
        return self.label


    def selectable(self):
        return True

    def keypress(self, *args, **kw):
        return self._hidden_btn.keypress(*args, **kw)

    def mouse_event(self, *args, **kw):
        return self._hidden_btn.mouse_event(*args, **kw)

if __name__ == "__main__":
    left_dash = urwid.Text(u"\u2588\u2588\u2580\u2588\u2588\u2588\u2588\u2588\u2580\u2588\u2588\u2588",'right')
    nav = BoxButton("a")
    right_dash = urwid.Text(u"\u2588\u2588\u2580\u2588\u2588\u2588\u2588\u2588\u2580\u2588\u2588\u2588\u2588\u2588\u2580\u2588\u2588\u2588",'left')
    finish_o = urwid.Filler(urwid.Padding(urwid.Columns([(urwid.BoxAdapter(urwid.Filler(left_dash,'middle'),7)),(11,nav),(right_dash)]),'center'))
    urwid.MainLoop(finish_o, palette=[('reversed', 'standout', '')]).run()
