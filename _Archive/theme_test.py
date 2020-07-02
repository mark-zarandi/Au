#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hjson

themes_dict = open("themes.hjson","r").read()
themes_dict = hjson.loads(themes_dict)
print(themes_dict['Themes']['Base']['buttons__c'])