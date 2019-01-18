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

FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
root = tkinter.Tk()  # where to open
root.withdraw() #open
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path

csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file

if len(csv_path) <1: #check for file picker cancel
    print("No file choosen, closing ...")
    sleep(2)
    sys.exit()

try:
    csvFile = pd.read_csv(csv_path) #load file
except:
    print("Could not open file, closing ...")
    sleep(2)
    sys.exit()

for index, row in csvFile.iterrows(): #duplicate header row check
    if row['first_name'] == 'first_name' and index > 1:
        print('deleting ' + str(row.name))
        csvFile.drop(index, inplace=True)
            
print (len(list(csvFile)))
for col in csvFile: #check for peasant columns
    value_counts = csvFile[col].count()
    if value_counts < 10:
        #print('deleting ' + col)
        del csvFile[col]
        
print (len(list(csvFile)))

try: # write file
    csvFile.to_csv(csv_path.replace('.csv', '_scrubbed.csv'))
    print("All done. Check location of original file for scrubbed file. Closing ...")
    sleep(2)
except:
    print("Could not save file, closing...")
    sleep(2)
    sys.exit()