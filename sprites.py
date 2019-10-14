
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
from banner import BannerHandler
from jishiHandler import jishiReader
from soco import groups

blank_column = [[0],[0],[0],[0],[0]]
pod_dict = open("buttons.hjson","r").read()
pod_dict = hjson.loads(pod_dict)
themes_dict = open("themes.hjson","r").read()
themes_dict = hjson.loads(themes_dict)
ansi_palette = [
    ('banner', '', '', '', '#ffa', '#60d'),
    ('streak', '', '', '', 'g50', '#60a'),
    ('inside', '', '', '', 'g38', '#808'),
    ('outside', '', '', '', 'g27', '#a06'),
    ('bg', '', '', '', 'g7', '#d06')]

class SpriteButton(urwid.WidgetWrap):
   
    def __init__(self, label, place_int=-1, on_press=None, user_data=None):
        _top_char = u'\u2580'
        _top_corner = u'\u2584'
        _bottom_char = u'\u2584'
        _bottom_corner = u'\u2580'
        padding_size = 2
        #move border calcs further down.
        
        lookie = lambda t: len(t)
        vfunc = numpy.vectorize(lookie)

        top_border = _top_corner + (_top_char * (15)) + _top_corner
        bottom_border = _bottom_corner + (_bottom_char * 15) + _bottom_corner
        cursor_position = len(top_border) + padding_size
        self.label = label
      
        ansi_word = []
           
        word_array = ansi_sprites[label]

        new_line = ''
        ansi_word.append(urwid.AttrMap(urwid.Text(top_border,align='center'),'#06a','bg'))

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

        super(SpriteButton, self).__init__(self.widget)
    def get_label_p(self):
        return self.label


    def selectable(self):
        return True

    def keypress(self, *args, **kw):
        return self._hidden_btn.keypress(*args, **kw)

    def mouse_event(self, *args, **kw):
        return self._hidden_btn.mouse_event(*args, **kw)

if __name__ =="__main__":
    ansi_palette = [
    ('banner', '', '', '', '#ffa', '#60d'),
    ('streak', '', '', '', 'g50', '#60a'),
    ('inside', '', '', '', 'g38', '#808'),
    ('outside', '', '', '', 'g27', '#a06'),
    ('bg', '', '', '', 'g7', '#d06')]

    left_button = SpriteButton('left',60)
    loop = urwid.MainLoop(
            urwid.Filler(urwid.Padding(left_button)), palette=ansi_palette)
    loop.run()
