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
from boxbutton import BoxButton
from soco.exceptions import SoCoUPnPException
import math
import random
import pickle
#level = logging.CRITICAL
#format   = '%(asctime)-8s %(levelname)-8s %(message)s'
#handlers = [logging.handlers.TimedRotatingFileHandler('/usr/local/bin/logs/screen_log',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None), logging.StreamHandler()]


blank_column = [[0],[0],[0],[0],[0]]
pod_dict = open("buttons.hjson","r").read()
pod_dict = hjson.loads(pod_dict)
themes_dict = open("themes.hjson","r").read()
themes_dict = hjson.loads(themes_dict)
dates_dict = None

def right(s, amount):
    return s[-amount:]

def theme_set():
    random_pick = (random.choice(list(themes_dict['Themes'])))
    random_pick = "Very_Blue"
    ansi_palette=[("clock_c","","","",f"",""),
    ("clock_c","","","",f"h{themes_dict['Themes'][random_pick]['clock_c']}",""),
    ("outer_box_c","","","",f"h{themes_dict['Themes'][random_pick]['outer_box_c']}",""),
    ("burger","","","",f"h{themes_dict['Themes'][random_pick]['burger_c']}",""),
    #buttons
    ("button_top_c","","","",f"h{themes_dict['Themes'][random_pick]['buttons_c']['top_c']}",""),
    ("button_bottom_c","","","",f"h{themes_dict['Themes'][random_pick]['buttons_c']['bottom_c']}",""),
    ("button_left_c","","","",f"h{themes_dict['Themes'][random_pick]['buttons_c']['left_c']}",""),
    ("button_right_c","","","",f"h{themes_dict['Themes'][random_pick]['buttons_c']['right_c']}",""),
    ("button_text_c","","","",f"h{themes_dict['Themes'][random_pick]['buttons_c']['text_c']}",""),
    #nav
    ("nav_top_c","","","",f"h{themes_dict['Themes'][random_pick]['nav']['top_c']}",""),
    ("nav_bottom_c","","","",f"h{themes_dict['Themes'][random_pick]['nav']['bottom_c']}",""),
    ("nav_left_c","","","",f"h{themes_dict['Themes'][random_pick]['nav']['left_c']}",""),
    ("nav_right_c","","","",f"h{themes_dict['Themes'][random_pick]['nav']['right_c']}",""),
    ("nav_text_c","","","",f"h{themes_dict['Themes'][random_pick]['nav']['text_c']}","")]

    return ansi_palette

def get_theme(stringer):
    nav_dict = {"nav":{"top_c":"nav_top_c",
                        "bottom_c":"nav_bottom_c",
                        "left_c":"nav_left_c",
                        "text_c":"nav_text_c"},
                "button":{"top_c":"button_top_c",
                        "bottom_c":"button_bottom_c",
                        "left_c":"button_left_c",
                        "text_c":"button_text_c"},
                "burger":{"top_c":"black",
                        "bottom_c":"black",
                        "left_c":"black",
                        "text_c":"burger"},}
    return nav_dict[stringer]

class Au:
    def flip_back(self):
        logging.info('splitting')
        flip_here = user_data_x['index_dict'] - 1
        flip_iter = 0
        for x in self.buttons_list[self.page_num][0]:
            if 'Pile' in str(type(x)):
                temp_holder = self.buttons_list[self.page_num][0][flip_iter]
                self.buttons_list[self.page_num][0][flip_iter] = self.buttons_list[self.page_num][1][flip_iter]
                self.buttons_list[self.page_num][1][flip_here] = temp_holder
            flip_iter += 1
        self.poor_man_refresh()

    #returns the SPLIT buttons
    def make_play_func(self,pod_id,index_id):

        def flip_back(x):
            logging.info('splitting')
            flip_here = x - 1
            flip_iter = 0
            for x in self.buttons_list[self.page_num][0]:
                if 'Pile' in str(type(x)):
                    temp_holder = self.buttons_list[self.page_num][0][flip_iter]
                    self.buttons_list[self.page_num][0][flip_iter] = self.buttons_list[self.page_num][1][flip_iter]
                    self.buttons_list[self.page_num][1][flip_iter] = temp_holder
                flip_iter += 1
            self.poor_man_refresh()

        def get_random(self):
            
            logging.info('getting random.')
            
            def play_it_ran():
                flip_back(index_id)
                logging.info('random threading')
                play_room = (str(pod_dict['Rooms']['Living']))
                url = 'http://0.0.0.0:5005/preset/all_rooms/'
                r = requests.get(url)
                data = requests.get('http://0.0.0.0:5000/random/' + str(pod_id) +"/").json()
                time.sleep(1)
                sonos = SoCo(play_room)
                sonos.play_uri(data['location'])

            #parallel threading
            t = threading.Thread(name="sonos_play_thread",target=play_it_ran)
            t.start()


        def get_recent(self):
            logging.info('getting recent')

            def play_it_rec():
                flip_back(index_id)
                logging.info('recent thread')
                url = 'http://0.0.0.0:5005/preset/all_rooms/'
                r = requests.get(url)
                play_room = (str(pod_dict['Rooms']['Living']))
                sonos = SoCo(play_room)
                data = requests.get('http://0.0.0.0:5000/recent/' + str(pod_id)).json() 
                sonos.play_uri(data['location'])
                sonos.play()

                    
                #parallel threading
            t = threading.Thread(name="sonos_play_thread",target=play_it_rec)
            t.start()


        #func_dict = {"recent":get_recent,"random":get_random}
        split_theme = get_theme("button")
        split_array = []
        split_array.append(BoxButton('recent',on_press=get_recent,show_date=False,user_data=None,theme=split_theme))
        split_array.append(urwid.Divider(" ",top=0,bottom=0))
        split_array.append(BoxButton('random',on_press=get_random,show_date=False,user_data=None,theme=split_theme))
        return urwid.Pile(split_array)

    def keypress(self, key):
        if self.menu_state == 'choosing':
            self.menu_state = "pods"
            self.page_num = 0
            self.menu_show = False
            self.force_refresh = True
            self.poor_man_refresh()
        if (key[0] == "mouse release") and self.menu_show:
            self.menu_state = 'choosing'
            #print(self.menu_show)

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def poor_man_refresh(self, what_to_do=True):
        temp_minute = datetime.datetime.now().minute
        if temp_minute < 10:
            temp_minute = "0" + str(temp_minute)
        else:
            temp_minute
        clock_element = urwid.AttrMap(urwid.BigText("{0}{1}{2}".format(datetime.datetime.now().hour,":",temp_minute), urwid.font.HalfBlock5x4Font()),"clock_c")
        burger = BoxButton('burger', 999, is_sprite=True,on_press=self.show_menu,no_border=True,user_data=None,theme=get_theme("burger"))
        button_line_box = urwid.AttrMap(urwid.LineBox(urwid.Pile([urwid.Divider(" ",top=0,bottom=0),urwid.GridFlow(self.buttons_list[self.page_num][0],cell_width=50,h_sep=0,v_sep=2,align='center'),urwid.Divider(" ",top=0,bottom=0)]),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588"),"outer_box_c")
        base = urwid.Filler(
                urwid.Pile([
                    urwid.Columns([urwid.Padding(clock_element, 'left', width='clip'),urwid.Padding(burger,'right',width=('relative',19))]),
                    button_line_box,
                    urwid.Divider(" ",top=0,bottom=0),
                    urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')]),'top')
        if what_to_do:
            self.loop.widget = base
        else: 
            return base

        


    def set_buttons(self, callbacker):
        logging.info('setting buttons')
        self.buttons_list = []
        index_dict = 1

        #whatever media, extract them to make an interable
        if self.menu_state == "spots":
            sonos = SoCo(pod_dict['Rooms']['Living'])
            
            page_split = pickle.load(open("sonos_pl.p","rb"))
            #print(page_split)
            #time.sleep(10)
        else:
            page_split = list(pod_dict["Pods"].items())
        
        #what's the size of the iterable.
        cards_size = len(page_split)

        # if (self.page_num * 6) < cards_size:
        #     finish = self.page_num * 6
        #     if self.page_num > 1:
        #         start = (finish)-6
        #     else:
        #         start = 0
        # else:
        #     finish = cards_size
        #     start = ((self.page_num * 6)) - 6
        temp_page = 0
        total_pages = math.ceil(cards_size/6)

        button_theme = get_theme('button')
        if self.menu_state == "spots":
            for x in range(0,int(total_pages)):
                index_dict = 1

                split_page_array = []
                back_button_array = []
                front_button_array = []
                for key in page_split:
                    value = {}
                    if math.ceil(index_dict/6)==(temp_page+1):
                        value["label"] = key.title
                        value['location'] = key.to_dict()['resources'][0]['uri']
                        value["index_dict"] = index_dict - (temp_page * 6)
                        new_button_front = BoxButton(value['label'], index_dict, on_press=callbacker,show_date=False,theme=button_theme,user_data=value)
                        front_button_array.append(new_button_front)
                    index_dict = index_dict + 1

                temp_page += 1

                split_page_array.append(front_button_array)
                split_page_array.append(back_button_array)
                self.buttons_list.append(split_page_array)
                #print((x.to_dict())['resources'][0]['uri'])
                    
        else:
            for x in range(0,int(total_pages)):    
                index_dict = 1
                split_page_array = []
                back_button_array = []
                front_button_array = []
                for key,value in page_split:
                    if math.ceil(index_dict/6)==(temp_page+1):
                        value["index_dict"] = index_dict - (temp_page * 6)

                        new_button_front = BoxButton(value['label'], index_dict, on_press=callbacker,show_date=False,theme=button_theme,user_data=value)
                        front_button_array.append(new_button_front)
                        new_button_back = self.make_play_func(value['pod_id'],value['index_dict'])
                        back_button_array.append(new_button_back)

                    index_dict = index_dict + 1

                temp_page += 1

                split_page_array.append(front_button_array)
                split_page_array.append(back_button_array)
                self.buttons_list.append(split_page_array)


                    #print('writing buttons')   


    def setup_view(self):
        logging.info('making buttons.')
        nav_theme = get_theme("nav") 
        def split(link,user_data_x):
            logging.info('splitting')
            flip_here = user_data_x['index_dict'] - 1
            flip_iter = 0
            for x in self.buttons_list[self.page_num][0]:
                if 'Pile' in str(type(x)):
                    temp_holder = self.buttons_list[self.page_num][0][flip_iter]
                    self.buttons_list[self.page_num][0][flip_iter] = self.buttons_list[self.page_num][1][flip_iter]
                    self.buttons_list[self.page_num][1][flip_iter] = temp_holder
                flip_iter += 1
            temp_holder = self.buttons_list[self.page_num][0][flip_here]
            self.buttons_list[self.page_num][0][flip_here] = self.buttons_list[self.page_num][1][flip_here]
            self.buttons_list[self.page_num][1][flip_here] = temp_holder
            self.poor_man_refresh()

            
        def play_sonos(junk):
            logging.info('play button pressed')

            self.force_refresh = True
            self.nav_array[int(right(junk.label,1))-1] = BoxButton('pause', 2, is_sprite=True,theme=nav_theme,on_press=pause_sonos,user_data=None)
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
            self.nav_array[int(right(junk.label,1))-1] = BoxButton('play', 2, is_sprite=True,theme=nav_theme,on_press=play_sonos,user_data=None)
            #self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for hotel testing
            play_room = (str(pod_dict['Rooms']['Living']))
            sonos = SoCo(play_room)
            sonos.group.coordinator.pause()

        def back_page(junk):
            if self.page_num > 0:
                self.page_num = self.page_num - 1
                self.poor_man_refresh()
            else:
                logging.info('page num error')

        def forward_page(junk):
            if self.page_num + 1 < len(self.buttons_list):
                self.page_num = self.page_num + 1
            #self.set_buttons(split)
                self.poor_man_refresh()
            else:
                print('too far')

        def lets_spot(junk):
            nav_theme = get_theme('nav')
            self.menu_state = "spots"
            self.page_num = 0
            self.set_buttons(play_spot)
            self.force_refresh = True
            self.menu_show = False
            self.menu_array[0] = (BoxButton('POD', 1, show_date=False,is_sprite=False,on_press=lets_pod,theme=nav_theme,user_data=None))
            self.poor_man_refresh()
            
        def lets_pod(junk):
            nav_theme = get_theme('nav')
            self.menu_state = "pods"
            self.page_num = 0
            self.set_buttons(split)
            self.force_refresh = True
            self.menu_show = False
            self.menu_array[0] = (BoxButton('music', 1, is_sprite=True,theme=nav_theme,on_press=lets_spot,user_data=None))
            self.poor_man_refresh()
            
        def play_spot(junk, location):
            print(location)
            time.sleep(5)
            # play_room = (str(pod_dict['Rooms']['Living']))

            # sonos = SoCo(play_room)
            # uri = location['location']
            # sonos.clear_queue()
            # sonos.add_uri_to_queue(uri=uri)
            # sonos.play_from_queue(index=0)
            # sonos.play_mode ="SHUFFLE_NOREPEAT"


        if self.menu_state == "pods":    
            self.set_buttons(split)
        else:
            self.set_buttons(play_spot)
        self.nav_array = []
        self.nav_array.append(BoxButton('rr-30', 1, is_sprite=True,on_press=back_page,theme=nav_theme,user_data=None))
        self.nav_array.append(BoxButton('pause', 2, is_sprite=True,on_press=pause_sonos,theme=nav_theme,user_data=None))
        self.nav_array.append(BoxButton('ff-30', 3, is_sprite=True,on_press=forward_page,theme=nav_theme,user_data=None))

        self.menu_array = []
        self.menu_array.append(BoxButton('music', 1, is_sprite=True,on_press=lets_spot,theme=nav_theme,user_data=None))
        self.menu_array.append(BoxButton('play', 2, is_sprite=True,on_press=play_sonos,theme=nav_theme,user_data=None))
        self.menu_array.append(BoxButton('ff-30', 3, is_sprite=True,on_press=forward_page,theme=nav_theme,user_data=None))
        try:
            self.poor_man_refresh(True)
        except:
            return self.poor_man_refresh(False)



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
            self.poor_man_refresh()
        
        def play_sonos(junk):
            logging.info('pause button pressed, start playing')
            self.force_refresh = True
            self.nav_array[1] = BoxButton('pause', 2, is_sprite=True,on_press=play_sonos,user_data=None)
            #self.nav_grid = urwid.GridFlow(self.nav_array,cell_width=50,h_sep=0,v_sep=0,align='center')
            self.dead_alarm = self.loop.set_alarm_in(.01,self.refresh)
            #commented out for testing at hotel
            play_room = (str(pod_dict['Rooms']['Living']))
            self.poor_man_refresh()
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
        screen = urwid.raw_display.Screen()
        screen.register_palette(theme_set())
        screen.set_terminal_properties(256)
        self.page_num = 0
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

            if self.menu_show:
                self.loop.widget = urwid.Overlay(
                urwid.AttrMap(
                urwid.Filler(urwid.Padding(
                urwid.LineBox(
                urwid.Pile(self.menu_array),trcorner=u"\u2584",tlcorner=u"\u2584",tline=u"\u2584",bline=u"\u2580",blcorner=u"\u2580",brcorner=u"\u2580",lline=u"\u2588",rline=u"\u2588"),
                align="center",width='pack'),'middle',height='pack',top=0,bottom=0),'default'),
                self.poor_man_refresh(False),align='center',width=25,valign='middle',height=23)
            else:
                self.poor_man_refresh()
            if self.force_close:
                raise urwid.ExitMainLoop()
                sys.exit()
            logging.info("{0}{1}".format('still refreshing: ',str(self.process.memory_info().rss)))

        self.dead_alarm = self.loop.set_alarm_in(1, self.refresh)


if __name__ == '__main__':
    au = Au()
    
    sys.exit(au.main())
