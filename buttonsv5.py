#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import logging
from logging import handlers
import os
import urwid
import time
import sys
import hjson
import json
import numpy
from ansi_alphabet import the_alphabet, ansi_sprites
import requests
from soco import SoCo
import threading
#from banner import BannerHandler
from jishiHandler import jishiReader
from soco import groups
import gc
#level = logging.CRITICAL
#format   = '%(asctime)-8s %(levelname)-8s %(message)s'
#handlers = [logging.handlers.TimedRotatingFileHandler('/usr/local/bin/logs/screen_log',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None), logging.StreamHandler()]


blank_column = [[0],[0],[0],[0],[0]]
pod_dict = open("buttons.hjson","r").read()
pod_dict = hjson.loads(pod_dict)
themes_dict = open("themes.hjson","r").read()
themes_dict = hjson.loads(themes_dict)

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
def right(s, amount):
    return s[-amount:]

class BoxButton(urwid.WidgetWrap):
   
    def __init__(self, label, place_int=-1, is_sprite=False, on_press=None, user_data=None):
        _top_char = u'\u2580'
        _top_corner = u'\u2584'
        _bottom_char = u'\u2584'
        _bottom_corner = u'\u2580'
        padding_size = 2
        #move border calcs further down.
        if is_sprite == False:
            x = line_split(label).split("_")
            lookie = lambda t: len(t)
            vfunc = numpy.vectorize(lookie)

            top_border = _top_corner + (_top_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)) + _top_corner
            pad_space = len(top_border)
            bottom_border = _bottom_corner + (_bottom_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)) + _bottom_corner
            cursor_position = len(top_border) + padding_size
        else: 
            top_border = _top_corner + (_top_char * (15)) + _top_corner
            bottom_border = _bottom_corner + (_bottom_char * 15) + _bottom_corner
            pad_space = 19
        
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

        if is_sprite == False:
            word_array = label_construct(line_split(label))
        else:
            word_array = ansi_sprites[label]

        new_line = ''
        top_border = urwid.AttrMap(urwid.Text(top_border,align='center'),'bg')

        for x in word_array:
            new_line = ""

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
            
            ansi_word.append(urwid.Text(new_line,align="center"))
        bottom_border = urwid.Text(bottom_border,align='center')
        left_border = urwid.AttrMap(urwid.Text(u'\u2588'+u'\n'+u'\u2588'+u'\n'+u'\u2588'+u'\n'+u'\u2588'+u'\n'+u'\u2588'),'outside')
        middle_part = urwid.Padding(urwid.Pile((top_border,urwid.Columns(((1,left_border),urwid.AttrMap(urwid.Pile(ansi_word),'bg'),(1,left_border))),bottom_border)),align='center',width=pad_space)

        self.widget = middle_part
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

class Au:
    

    def keypress(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def setup_view(self):
        logging.info('making buttons.')
        self.clock_txt = urwid.BigText(time.strftime('%H:%M:%S'), urwid.font.HalfBlock5x4Font())
        self.clock_box = urwid.Padding(self.clock_txt, 'left', width='clip')
        
    

        def split(link,user_data_x):
            logging.info('splitting')

            
            def get_random(link, user_data=None):
                
                logging.info('getting random.')
                
                def play_it_ran():
                    logging.info('random threading')
                    play_room = (str(pod_dict['Rooms']['Master']))
                    url = 'http://0.0.0.0:5005/preset/all_rooms/'
                    r = requests.get(url)
                    data = requests.get('http://0.0.0.0:5000/random/' + str(user_data) +"/").json()
                    
                    time.sleep(1)


                    sonos = SoCo(play_room)
                
                    sonos.play_uri(data['location'])
                #parallel threading
                t = threading.Thread(name="sonos_play_thread",target=play_it_ran)
                t.start()

                set_buttons()

            def get_recent(link, user_data):
                logging.info('getting recent')
                def play_it_rec():
                    logging.info('recent thread')
                    url = 'http://0.0.0.0:5005/preset/all_rooms/'
                    r = requests.get(url)
                    play_room = (str(pod_dict['Rooms']['Master']))
                
                    data = requests.get('http://0.0.0.0:5000/recent/' + str(user_data)).json()
                    
                    sonos = SoCo(play_room)
                
                    sonos.play_uri(data['location'])
                    sonos.play()
                #parallel threading
                t = threading.Thread(name="sonos_play_thread",target=play_it_rec)
                t.start()
                set_buttons()
                
            set_buttons()
            split_array = []
            #add eval to compute strings.
            split_array.append(BoxButton('a',on_press=eval(user_data_x['method'][0]),user_data=user_data_x['pod_id']))
            split_array.append(BoxButton('b',on_press=eval(user_data_x['method'][1]),user_data=user_data_x['pod_id']))
            self.clock_txt = urwid.BigText(time.strftime('%H:%M:%S'), urwid.font.HalfBlock5x4Font())
            self.clock_box = urwid.Padding(self.clock_txt, 'left', width='clip')
            self.buttons_list[int(right(link.label,1))] = urwid.Columns(split_array)
            self.button_grid = urwid.GridFlow(self.buttons_list,50,0,2,'center')
            self.top_button_box = urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=2),self.button_grid,urwid.Divider(" ",top=0,bottom=2)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
            self.view = urwid.Filler(urwid.AttrMap(urwid.Pile([self.clock_box,self.top_button_box]),'body'),'middle')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            
        def play_sonos(junk):
            logging.info('play button pressed')
            self.nav_array[int(right(junk.label,1))-1] = BoxButton('pause', 2, is_sprite=True,on_press=pause_sonos,user_data=None)
            self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for testing at hotel
            #play_room = (str(pod_dict['Rooms']['Master']))
            #sonos = SoCo(play_room)
            #sonos.group.coordinator.play()

        def pause_sonos(junk):
            logging.info('pause pressed')
            self.nav_array[int(right(junk.label,1))-1] = BoxButton('play', 2, is_sprite=True,on_press=play_sonos,user_data=None)
            self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for hotel testing
            #play_room = (str(pod_dict['Rooms']['Master']))
            #sonos = SoCo(play_room)
            #sonos.group.coordinator.pause()

        def set_buttons():
            logging.info('setting buttons')
            self.buttons_list = []
            index_dict = 0 
            for key,value in pod_dict['Pods'].items():
                #remember, arguments can't be passed to callback through ON_PRESS, must use USER_DATE
                #print(len(value['method']))
                new_button = BoxButton(value['label'], index_dict, on_press=split,user_data=value)
                self.buttons_list.append(new_button)
                index_dict = index_dict + 1
                #print('writing buttons')    
        set_buttons()
        self.button_grid = urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=2,v_sep=0,align='center')
        self.nav_array = []
        self.nav_array.append(BoxButton('rr-30', 1, is_sprite=True,on_press=pause_sonos,user_data=None))
        self.nav_array.append(BoxButton('play', 2, is_sprite=True,on_press=play_sonos,user_data=None))
        self.nav_array.append(BoxButton('ff-30', 3, is_sprite=True,on_press=pause_sonos,user_data=None))
        self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
        self.top_button_box = urwid.LineBox(self.button_grid,trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
        self.view = urwid.Filler(urwid.AttrMap(urwid.Pile([self.clock_box,self.top_button_box,self.nav_grid]),'body'),'middle')

    


    def main(self):
        #jish_run = jishiReader('./node-sonos/package.json')
        level    = logging.NOTSET
        format   = '%(asctime)-8s %(levelname)-8s %(message)s'
        handlers = [logging.handlers.TimedRotatingFileHandler('button_log',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None)]
        ansi_palette = [('banner', '', '', '', '#ffa', '#60d'),
    ('streak', '', '', '', 'g50', '#60a'),
    ('inside', '', '', '', 'g38', '#808'),
    ('outside', '', '', '', 'g27', '#a06'),
    ('bg', '', '', '', '#d06', 'g7')]
        logging.basicConfig(level = level, format = format, handlers = handlers)
        screen = urwid.raw_display.Screen()
        screen.register_palette(ansi_palette)
        screen.set_terminal_properties(256)
        self.setup_view()
        logging.warning("starting up.")
        self.loop = urwid.MainLoop(
            self.view,screen=screen,
            unhandled_input=self.keypress)
        self.process = psutil.Process(os.getpid())
        self.loop_count = 0
        self.dead_alarm = self.loop.set_alarm_in(.2, self.refresh)
        self.loop.start()
        self.loop.run()

    def refresh(self, loop=None, data=None):
        self.loop_count = self.loop_count + 1
        self.loop.remove_alarm(self.dead_alarm)
        self.button_grid = urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=2,align='center')
        self.clock_txt = urwid.BigText(time.strftime('%H:%M:%S'), urwid.font.HalfBlock5x4Font())
        self.clock_box = urwid.Padding(self.clock_txt, 'left', width='clip')
        self.top_button_box = urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=2),self.button_grid,urwid.Divider(" ",top=0,bottom=2)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588")
        self.view = urwid.Filler(urwid.Pile([self.clock_box,self.top_button_box,urwid.Divider(" ",top=0,bottom=1),self.nav_grid]),'middle')
        self.loop.widget = self.view
        if (self.loop_count % 10) == 0:
            logging.info('still refreshing: ' + str(self.process.memory_info().rss))
            gc.collect()
            #MAYBE use with resurrect: raise urwid.ExitMainLoop()
        self.dead_alarm = self.loop.set_alarm_in(1, self.refresh)


if __name__ == '__main__':
    au = Au()
    
    sys.exit(au.main())
