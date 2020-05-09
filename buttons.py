#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import logging
from logging import handlers
import os
import urwid
import time
import datetime
import sys
import hjson
import json
import numpy
from resources import the_alphabet, ansi_sprites
import requests
from soco import SoCo
import threading
import socketio
from soco import groups
import gc
from soco.exceptions import SoCoUPnPException
#level = logging.CRITICAL
#format   = '%(asctime)-8s %(levelname)-8s %(message)s'
#handlers = [logging.handlers.TimedRotatingFileHandler('/usr/local/bin/logs/screen_log',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None), logging.StreamHandler()]


blank_column = [[0],[0],[0],[0],[0]]
pod_dict = open("buttons.hjson","r").read()
pod_dict = hjson.loads(pod_dict)
themes_dict = open("themes.hjson","r").read()
themes_dict = hjson.loads(themes_dict)
dates_dict = None

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
   
    def __init__(self, label, place_int=-1, show_date=True, is_sprite=False, on_press=None, user_data=None, no_border = False, themes=None):
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

            top_border = ("{0}{1}{2}").format(_top_corner,(_top_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)),_top_corner)
            pad_space = len(top_border)
            bottom_border = ("{0}{1}{2}").format(_bottom_corner,(_bottom_char * (((max(vfunc(x)) * 5) + max(vfunc(x))-1) + padding_size)),_bottom_corner)
            cursor_position = len(top_border) + padding_size
        else: 
            top_border = ("{0}{1}{2}").format(_top_corner,(_top_char * (15)),_top_corner)
            bottom_border = ("{0}{1}{2}").format(_bottom_corner,(_bottom_char * 15),_bottom_corner)
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
            bottom_date = urwid.Text("01/01/2019 12:00",align='center')
        else:
            word_array = ansi_sprites[label]
            bottom_date = None
        #border attributes here.
        new_line = ''
        top_border = urwid.AttrMap(urwid.Text(top_border,align='center'),'top_c')
        bottom_border = urwid.Text(bottom_border,align='center')
        left_border = urwid.AttrMap(urwid.Text(u'\u2588'+u'\n'+u'\u2588'+u'\n'+u'\u2588'+u'\n'+u'\u2588'+u'\n'+u'\u2588'),'left_c')
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
                7:u"\u2594",#upper 1/8
                8:u"\u259D",#quad right
                9:u"\u2598",
                11:u"\u2589",
                10:u"\u258F",
                15:u"\u2582",
                12:u"\u258C",
                13:u"\u259E", #diag right
                14:u"\u259A", #diag left
                20:u"\u2599" #quad upleft
                }
                new_line = ("{0}{1}").format(new_line,switcher.get(y))
            #for blink, put attrmap here.
            ansi_word.append(urwid.Text(new_line,align="center"))

        #text attributes here       
        if is_sprite == False:
            if show_date:
                middle_part = urwid.Padding(urwid.Pile((top_border,urwid.Columns(((1,left_border),urwid.AttrMap(urwid.Pile(ansi_word),'text_c'),(1,left_border))),bottom_border,bottom_date)),align='center',width=pad_space)
            else:
                middle_part = urwid.Padding(urwid.Pile((top_border,urwid.Columns(((1,left_border),urwid.AttrMap(urwid.Pile(ansi_word),'text_c'),(1,left_border))),bottom_border)),align='center',width=pad_space)
        else:
            if not no_border:
                middle_part = urwid.Padding(urwid.Pile((top_border,urwid.Columns(((1,left_border),urwid.AttrMap(urwid.Pile(ansi_word),'text_c'),(1,left_border))),bottom_border)),align='center',width=pad_space)
            else:
                middle_part = urwid.Padding(urwid.AttrMap(urwid.Pile(ansi_word),'text_c'),align='center',width=pad_space)
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
   



#    def start_up(self,loop=None, data=None):
#        sio = socketio.Client()
#        @sio.event
#        def connect():
#            logging.warning("connection established")
#
#
#        @sio.on('message')
#        def on_message(data):
#            sio.disconnect()
#            self.force_refresh = True
#            self.force_close = True
#            self.loop.set_alarm_in(.2, self.refresh)

        #     raise urwid.ExitMainLoop()


        # sio.connect('ws://localhost:5000')
        # sio.wait()

    def keypress(self, key):
        if self.menu_state == 'choosing':
            self.menu_state = "pods"
            self.page_num = 1
            self.menu_show = False
            self.force_refresh = True
            self.refresh()
        if (key[0] == "mouse release") and self.menu_show:
            self.menu_state = 'choosing'
            #print(self.menu_show)

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        


    def set_buttons(self, callbacker):
        logging.info('setting buttons')
        self.buttons_list = []
        index_dict = 0
        if self.menu_state == "spots":
            sonos = SoCo(pod_dict['Rooms']['Living'])
            sonos_playlists = sonos.get_sonos_playlists()
            page_split = list(sonos_playlists)
        else:
            page_split = list(pod_dict["Pods"].items())
        cards_size = len(page_split)
        if (self.page_num * 6) < cards_size:
            finish = self.page_num * 6
            if self.page_num > 1:
                start = (finish)-6
            else:
                start = 0
        else:
            finish = cards_size
            start = ((self.page_num * 6)) - 6
            
        if self.menu_state == "spots":
            for x in page_split[start:finish]:
                #print((x.to_dict())['resources'][0]['uri'])
                fix_length = (x.to_dict())['title']
                new_button = BoxButton(fix_length, index_dict, on_press=callbacker,show_date=False,user_data=(x.to_dict())['resources'][0]['uri'])
                self.buttons_list.append(new_button)
                index_dict = index_dict + 1
        else:    
            for key,value in page_split[start:finish]:
                #remember, arguments can't be passed to callback through ON_PRESS, must use USER_DATE
                #print(len(value['method']))

                #removed dates for the time being
                new_button = BoxButton(value['label'], index_dict, on_press=callbacker,show_date=False,user_data=value)
                self.buttons_list.append(new_button)
                index_dict = index_dict + 1
                #print('writing buttons')   


    def setup_view(self):
        logging.info('making buttons.')

        def split(link,user_data_x):
            logging.info('splitting')

            def blink(link,user_data = None):
                return None

            def get_random(link, user_data=None):
                
                logging.info('getting random.')
                
                def play_it_ran():
                    logging.info('random threading')
                    play_room = (str(pod_dict['Rooms']['Living']))
                    url = 'http://0.0.0.0:5005/preset/all_rooms/'
                    r = requests.get(url)
                    data = requests.get('http://0.0.0.0:5000/random/' + str(user_data) +"/").json()
                    
                    time.sleep(1)


                    sonos = SoCo(play_room)
                
                    sonos.play_uri(data['location'])
                #parallel threading
                t = threading.Thread(name="sonos_play_thread",target=play_it_ran)
                t.start()

                self.set_buttons(split)
                self.force_refresh = True

            def get_recent(link, user_data):
                logging.info('getting recent')
                def play_it_rec():
                    logging.info('recent thread')
                    url = 'http://0.0.0.0:5005/preset/all_rooms/'
                    r = requests.get(url)
                    play_room = (str(pod_dict['Rooms']['Living']))
                    sonos = SoCo(play_room)
                    data = requests.get('http://0.0.0.0:5000/recent/' + str(user_data)).json() 
                    sonos.play_uri(data['location'])
                    sonos.play()
                    
                #parallel threading
                t = threading.Thread(name="sonos_play_thread",target=play_it_rec)
                t.start()
                self.set_buttons(split)
                self.force_refresh = True
            if self.menu_state == "pods":    
                self.set_buttons(split)
            else:
                self.set_buttons(lets_spot)

            split_array = []
            #add eval to compute strings.
            split_array.append(BoxButton('recent',on_press=eval(user_data_x['method'][0]),show_date=False,user_data=user_data_x['pod_id']))
            split_array.append(urwid.Divider(" ",top=0,bottom=0))
            split_array.append(BoxButton('random',on_press=eval(user_data_x['method'][1]),show_date=False,user_data=user_data_x['pod_id']))
            
            self.buttons_list[int(right(link.label,1))] = urwid.Pile(split_array)
            temp_minute = datetime.datetime.now().minute
            if temp_minute < 10:
                temp_minute = "0" + str(temp_minute)
            else:
                temp_minute
            base = urwid.Filler(
                urwid.Pile([
                    urwid.Columns([urwid.Padding(urwid.BigText("{0}{1}{2}".format(datetime.datetime.now().hour,":",temp_minute), urwid.font.HalfBlock5x4Font()), 'left', width='clip'),urwid.Padding(BoxButton('burger', 999, is_sprite=True,on_press=self.show_menu,no_border=True,user_data=None),'right',width=('relative',19))]),
                    urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=0),
        
                    urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=2,align='center'),
                    urwid.Divider(" ",top=0,bottom=0)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588"),
                    urwid.Divider(" ",top=0,bottom=0),
                    urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')]),'top')
            self.loop.widget = base
            self.dead_alarm = self.loop.set_alarm_in(1, self.refresh)
            #self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            
        def play_sonos(junk):
            logging.info('play button pressed')

            self.force_refresh = True
            self.nav_array[int(right(junk.label,1))-1] = BoxButton('pause', 2, is_sprite=True,on_press=pause_sonos,user_data=None)
            #self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for testing at hotel
            play_room = (str(pod_dict['Rooms']['Living']))
            try:
                sonos = SoCo(play_room)
                look_at_queue = sonos.get_queue()
                print('lets play')
                if len(look_at_queue)>0:
                    sonos.group.coordinator.play()
                #else:
                #    print("the queue is empty")
            except:
                #this doesn't work for some reason. try just looking for stop states.
                logger.warning("Exception caught. Not expecting trace", exc_info=False, stack_info=False)
                print("the queue is empty")



        def pause_sonos(junk):
            logging.info('pause pressed')
            self.force_refresh = True
            self.nav_array[int(right(junk.label,1))-1] = BoxButton('play', 2, is_sprite=True,on_press=play_sonos,user_data=None)
            #self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for hotel testing
            play_room = (str(pod_dict['Rooms']['Living']))
            sonos = SoCo(play_room)
            sonos.group.coordinator.pause()

        def back_page(junk):
            if self.page_num > 1:
                self.page_num = self.page_num - 1
                self.set_buttons(split)
                self.force_refresh=True
                self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            else:
                logging.info('page num error')

        def forward_page(junk):
            self.page_num = self.page_num + 1
            self.set_buttons(split)
            self.force_refresh=True
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)

        def lets_spot(junk):
            self.menu_state = "spots"
            self.page_num = 1
            self.set_buttons(play_spot)
            self.force_refresh = True
            self.menu_show = False
            self.menu_array[0] = (BoxButton('T', 1, is_sprite=False,on_press=lets_pod,user_data=None))
            self.dead_alarm = self.loop.set_alarm_in(1, self.refresh)
            
        def lets_pod(junk):
            self.menu_state = "pods"
            self.page_num = 1
            self.set_buttons(split)
            self.force_refresh = True
            self.menu_show = False
            self.menu_array[0] = (BoxButton('music', 1, is_sprite=True,on_press=lets_spot,user_data=None))
            self.dead_alarm = self.loop.set_alarm_in(1, self.refresh) 
            
            
            
        def play_spot(junk, location):
            play_room = (str(pod_dict['Rooms']['Living']))

            sonos = SoCo(play_room)
            uri = location
            sonos.clear_queue()
            sonos.add_uri_to_queue(uri=uri)
            sonos.play_from_queue(index=0)
            sonos.play_mode ="SHUFFLE_NOREPEAT"

 
        if self.menu_state == "pods":    
            self.set_buttons(split)
        else:
            self.set_buttons(play_spot)

        self.nav_array = []
        self.nav_array.append(BoxButton('rr-30', 1, is_sprite=True,on_press=back_page,user_data=None))
        self.nav_array.append(BoxButton('pause', 2, is_sprite=True,on_press=pause_sonos,user_data=None))
        self.nav_array.append(BoxButton('ff-30', 3, is_sprite=True,on_press=forward_page,user_data=None))

        self.menu_array = []
        self.menu_array.append(BoxButton('music', 1, is_sprite=True,on_press=lets_spot,user_data=None))
        self.menu_array.append(BoxButton('play', 2, is_sprite=True,on_press=play_sonos,user_data=None))
        self.menu_array.append(BoxButton('ff-30', 3, is_sprite=True,on_press=forward_page,user_data=None))

        return urwid.Filler(
                urwid.Pile([
                    urwid.Padding(urwid.BigText(time.strftime('%H:%M'), urwid.font.HalfBlock5x4Font()), 'left', width='clip'),
                    urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=2),urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=2,align='center'),urwid.Divider(" ",top=0,bottom=2)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588"),
                    urwid.Divider(" ",top=0,bottom=1),
                    urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')]),'middle')


    def theme_set(self):

        self.ansi_palette=[("clock_c","","","",f"",""),
        ("clock_c","","","",f"h{themes_dict['Themes']['Base']['clock_c']}",""),
        ("outer_box_c","","","",f"h{themes_dict['Themes']['Base']['outer_box_c']}",""),
        ("top_c","","","",f"h{themes_dict['Themes']['Base']['buttons_c']['top_c']}",""),
        ("bottom_c","","","",f"h{themes_dict['Themes']['Base']['buttons_c']['bottom_c']}",""),
        ("left_c","","","",f"h{themes_dict['Themes']['Base']['buttons_c']['left_c']}",""),
        ("right_c","","","",f"h{themes_dict['Themes']['Base']['buttons_c']['right_c']}",""),
        ("text_c","","","",f"h{themes_dict['Themes']['Base']['buttons_c']['text_c']}","")]

    def is_playing(self, state):
        def pause_sonos(junk):
            logging.info('pause pressed')
            self.force_refresh = True
            self.nav_array[1] = BoxButton('play', 2, is_sprite=True,on_press=pause_sonos,user_data=None)
            #self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for hotel testing
            play_room = (str(pod_dict['Rooms']['Living']))
            sonos = SoCo(play_room)
            sonos.group.coordinator.pause()
            self.force_refresh = True
            self.dead_alarm = self.loop.set_alarm_in(.2, self.refresh)
        
        def play_sonos(junk):
            logging.info('pause button pressed, start playing')
            self.force_refresh = True
            self.nav_array[1] = BoxButton('pause', 2, is_sprite=True,on_press=play_sonos,user_data=None)
            #self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for testing at hotel
            play_room = (str(pod_dict['Rooms']['Living']))
            self.force_refresh = True
            self.dead_alarm = self.loop.set_alarm_in(.2, self.refresh)
            try:
                sonos = SoCo(play_room)
                look_at_queue = sonos.get_queue()

                if len(look_at_queue)>0:
                    sonos.group.coordinator.play()
                else:
                    print("the queue is empty")
            except soco.exceptions.SoCoUPnPException as e:
                logger.warning("Exception caught. Not expecting trace", exc_info=False, stack_info=False)
                print("the queue is empty")


        if state == "PLAYING":
            self.nav_array[1] = BoxButton('pause', 2, is_sprite=True,on_press=pause_sonos,user_data=None)
        else:
            self.nav_array[1] = BoxButton('play', 2, is_sprite=True,on_press=play_sonos,user_data=None)
        # #pause music here,.
        self.force_refresh = True
        self.dead_alarm = self.loop.set_alarm_in(.2, self.refresh)


    def main(self):
        level    = logging.NOTSET
        format   = '%(asctime)-8s %(levelname)-8s %(message)s'
        handlers = [logging.handlers.TimedRotatingFileHandler('button_log',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None)]
        #ansi_palette = [('banner', '', '', '', '#ffa', '#60d'),
    #('streak', '', '', '', 'g50', '#60a'),
    #('inside', '', '', '', 'g38', '#808'),
    #('outside', '', '', '', 'h26', '#a06'),
    #('bg', '', '', '', 'h46', 'g0')]
        logging.basicConfig(level = level, format = format, handlers = handlers)
        self.theme_set()
        screen = urwid.raw_display.Screen()
        screen.register_palette(self.ansi_palette)
        screen.set_terminal_properties(256)
        self.page_num = 1
        self.menu_state = "pods"
        x_test = self.setup_view()
        logging.warning("starting up.")
        self.loop = urwid.MainLoop(
            x_test,screen=screen,
            unhandled_input=self.keypress)
        self.process = psutil.Process(os.getpid())
        self.menu_show = False
        
        self.minute_lock = datetime.datetime.now().minute
        self.dead_alarm = self.loop.set_alarm_in(.2, self.refresh)
        self.force_refresh = True
        self.force_close = False

        self.loop.run()
    
    def get_out(self):
        self.force_refresh = True
        self.force_close = True
        self.dead_alarm = self.loop.set_alarm_in(.2, self.refresh)

    def change_global_dates(self, new_date):
        return None
    
    #socketio coroutine test, will this run?

        #self.dead_alarm = self.loop.set_alarm_in(1, self.refresh)
        #self.loop.remove_alarm(self.dead_alarm)
    def show_menu(self, junk):

        self.force_refresh = True
        self.menu_show = True
        self.refresh()

    def refresh(self, loop=None, data=None):

            
        self.loop.remove_alarm(self.dead_alarm)
        temp_minute = datetime.datetime.now().minute
        if (temp_minute != self.minute_lock) or self.force_refresh or self.force_close:
            self.force_refresh = False
            self.minute_lock = temp_minute
            if temp_minute < 10:
                temp_minute = "0" + str(temp_minute)
            #for side to side navbar, consider passing buttnons_list to a function and have it return based on composition.
            base = urwid.Filler(
                urwid.Pile([
                    urwid.Columns([urwid.Padding(urwid.AttrMap(urwid.BigText("{0}{1}{2}".format(datetime.datetime.now().hour,":",temp_minute), urwid.font.HalfBlock5x4Font()),'clock_c'), 'left', width='clip'),urwid.Padding(BoxButton('burger', 999, is_sprite=True,on_press=self.show_menu,no_border=True,user_data=None),'right',width=('relative',19))]),
                    urwid.AttrMap(
                    urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=0),
                    urwid.GridFlow(self.buttons_list,cell_width=50,h_sep=0,v_sep=2,align='center'),
                    urwid.Divider(" ",top=0,bottom=2)]),
                    trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588"),'outer_box_c'),
                    urwid.Divider(" ",top=0,bottom=0),
                    urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')]),'top')          #,align='center',width=23,valign='middle',height=4)
            
            if self.menu_show:
                self.loop.widget = urwid.Overlay(
                urwid.AttrMap(
                urwid.Filler(urwid.Padding(
                urwid.LineBox(
                urwid.Pile(self.menu_array),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588"),
                align="center",width='pack'),'middle',height='pack',top=0,bottom=0),'default'),
                base,align='center',width=25,valign='middle',height=23)
            else:
                self.loop.widget = base
            if self.force_close:

                raise urwid.ExitMainLoop()
                sys.exit()
            logging.info("{0}{1}".format('still refreshing: ',str(self.process.memory_info().rss)))
            #gc.collect()
            gc.collect()
            #MAYBE use with resurrect: raise urwid.ExitMainLoop()
        self.dead_alarm = self.loop.set_alarm_in(1, self.refresh)


if __name__ == '__main__':
    au = Au()
    
    sys.exit(au.main())
