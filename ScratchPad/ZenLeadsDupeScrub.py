'''
scrubs un-needed info from contact export.
Say goodbye to duplicate, empty columns and that pesky duplicate header row!!
'''

import csv, os,sys
import tkinter  # for the file picker
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime
import pandas as pd
import numpy as np
from time import sleep

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
        
    print('\n')

FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
root = tkinter.Tk()  # where to open
root.withdraw() #open
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path
data = []

csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file

if len(csv_path) <1: #check for file picker cancel
    print("No file choosen, closing ...")
    sleep(2)
    sys.exit()

try:
    df = pd.read_csv(csv_path, low_memory = False, encoding = 'utf-8') #load file
except:
    print("Could not open file, closing ...")
    sleep(2)
    sys.exit()

data = df.set_index('id').T.to_dict('list')
for key in data:
    for i in range(len(data[key])):
        data[key][i] = str(data[key][i])