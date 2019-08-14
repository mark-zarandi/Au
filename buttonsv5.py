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
from soco import SoCo
import threading
from colored import fg, bg, attr

from soco import groups

blank_column = [[0],[0],[0],[0],[0]]
pod_dict = open("buttons.hjson","r").read()
pod_dict = hjson.loads(pod_dict)
themes_dict = open("themes.hjson","r").read()
themes_dict = hjson.loads(themes_dict)

def line_split(input_string):
    print(input_string)
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
        _bottom_char = u'\u2584'
        padding_size = 2
        #move border calcs further down.
        print('init')
        x = line_split(label).split("_")
        lookie = lambda t: len(t)
        vfunc = numpy.vectorize(lookie)

        top_border = _top_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)
        bottom_border = _bottom_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)
        cursor_position = len(top_border) + padding_size
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
            new_line = '\u2588' + '\u0020' + '\u0020'
            for y in x:
                #1 Full Block
                #2 Half Top Block
                #0 Space
                #3 Half Bottom Block
                
                
                switcher = {1:"\u2588",0:"\u0020",2:"\u2580",3:"\u2584"}
                new_line = new_line + switcher.get(y)
            new_line = new_line + '\u0020' + '\u2588'# + u"\n"
            ansi_word.append(urwid.Text(new_line,align="center"))
        ansi_word.append(urwid.Text(bottom_border,align='center'))
        self.widget = urwid.Pile(ansi_word)

        #self.widget = urwid.AttrMap(self.widget, '', 'highlight')

        # self.widget = urwid.Padding(self.widget, 'center')
        # self.widget = urwid.Filler(self.widget)

        # here is a lil hack: use a hidden button for evt handling
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

class Clock:
    

    def keypress(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def setup_view(self):
        self.clock_txt = urwid.BigText(time.strftime('%H:%M:%S'), urwid.font.HalfBlock5x4Font())
        self.clock_box = urwid.Padding(self.clock_txt, 'left', width='clip')
        
        def split(link,user_data_x):
            
            def right(s, amount):
                return s[-amount:]
            
            def get_random(link, user_data=None):
                
                #JISHI NODE SONOS NOT SETUP
                #url = 'http://localhost:5005/preset/all_rooms'
                #r = requests.get(url)
    
                
                def play_it():
                    play_room = (str(pod_dict['Rooms']['Master']))
                
                    r = requests.get('http://localhost:5000/random/' + str(user_data))
                    data = r.json()
                    sonos = SoCo(play_room)
                
                    sonos.play_uri(data['location'])
                #parallel threading
                t = threading.Thread(name="sonos_play_thread",target=play_it)
                t.start()

                set_buttons()

            def get_recent(link, user_data):
                print(user_data)

            set_buttons()
            split_array = []
            #add eval to compute strings.
            split_array.append(BoxButton('a',on_press=eval(user_data_x['method'][0]),user_data=user_data_x['pod_id']))
            split_array.append(BoxButton('b',on_press=get_recent,user_data=user_data_x))
            self.clock_txt = urwid.BigText(time.strftime('%H:%M:%S'), urwid.font.HalfBlock5x4Font())
            self.clock_box = urwid.Padding(self.clock_txt, 'left', width='clip')
            self.buttons_list[int(right(link.label,1))] = urwid.Columns(split_array)
            self.button_grid = urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.top_button_box = urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=2),self.button_grid,urwid.Divider(" ",top=0,bottom=2)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
            self.view = urwid.Filler(urwid.AttrMap(urwid.Pile([self.clock_box,self.top_button_box]),'body'),'middle')
            self.loop.set_alarm_in(.01,self.refresh)

        def set_buttons():

            self.buttons_list = []
            index_dict = 0 
            for key,value in pod_dict['Pods'].items():
                #remember, arguments can't be passed to callback through ON_PRESS, must use USER_DATE
                new_button = BoxButton(value['label'], index_dict, on_press=split,user_data=value)
                self.buttons_list.append(new_button)
                index_dict = index_dict + 1
                #print('writing buttons')    
        set_buttons()
        self.button_grid = urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=0,align='center')
        self.top_button_box = urwid.LineBox(self.button_grid,trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
        self.view = urwid.Filler(urwid.AttrMap(urwid.Pile([self.clock_box,self.top_button_box]),'body'),'middle')

    


    def main(self):
        
        self.setup_view()
        
        self.loop = urwid.MainLoop(
            self.view, palette=[('body', 'dark cyan', '')],
            unhandled_input=self.keypress)
        
        
        self.loop.set_alarm_in(.2, self.refresh)
        self.loop.run()

    def refresh(self, loop=None, data=None):
        self.button_grid = urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=0,align='center')
        self.clock_txt = urwid.BigText(time.strftime('%H:%M:%S'), urwid.font.HalfBlock5x4Font())
        self.clock_box = urwid.Padding(self.clock_txt, 'left', width='clip')
        self.top_button_box = urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=2),self.button_grid,urwid.Divider(" ",top=0,bottom=2)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
        self.view = urwid.Filler(urwid.AttrMap(urwid.Pile([self.clock_box,self.top_button_box]),'body'),'middle')
        self.loop.widget = self.view
        self.loop.set_alarm_in(1, self.refresh)


if __name__ == '__main__':
    clock = Clock()
    sys.exit(clock.main())