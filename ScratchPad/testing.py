#!/usr/bin/env python
'''
Created on Nov 16, 2016

@author: jchavis
'''
import datetime  # for comparing time stamps
import os, ctypes, tkinter
import requests, json
import csv

def today():
    today = datetime.datetime.now()
    return today.strftime('%Y-%m-%d')

print(today())