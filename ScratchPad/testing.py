#!/usr/bin/env python
'''
Created on Nov 16, 2016

@author: jchavis
'''
import datetime  # for comparing time stamps
import os, ctypes, tkinter
import requests, json
import csv

tagObj = {}
vals = []
value = "Mytags"
vals.append(value)
tagObj['Tags'] = vals
print(tagObj)
    
    