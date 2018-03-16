'''
Created on Jan 20, 2017

@author: jchavis

This module will take a CSV list of emails, find all associated
base id's for leads and delete those leads...eventually
'''

import datetime  # for comparing time stamps
import os, ctypes, sys
import requests, json
import csv
import argparse
import tkinter.filedialog as fd  # for picking the file
import tkinter as tk
import basecrm

def getToken():
    """this method will attempt to find a file containing the API token"""
    path = ""
    if(os.path.isfile("C:\\Apps\\NiceOffice\\token")):#search C:\Apps 
        path = "C:\\Apps\\NiceOffice\\token" # Found it! Load it
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + \
                        "\\noe\\token")): # search shared NOE folder
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token"
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + \
                        "\\NiceOffice\\token")): #the OTHER NOE location
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token"
    else: #token is not found in another location, ask the user to find it
        ctypes.windll.user32.MessageBoxW(0, "A token file was not "
                                          +"found in your NOE folder, "
                                          +"please choose the token file",
                                           "Token File", 0)
        FILEOPENOPTIONS = dict(filetypes=[('TOKEN file', '*.*')],
                               title=['Choose token file'])
        root = tkinter.Tk()  # where to open
        root.withdraw()
        # withdraw()  # hide Frame
        path = tkinter.filedialog.askopenfilename(**FILEOPENOPTIONS)# pick
    if(path == ""): # if not path was chosen, quit
        ctypes.windll.user32.MessageBoxW(0, "No file was chosen, quiting",
                                         "Token File", 0)
        exit()
    
    # read in the token from the file and return the token as a string
    file = open(path, 'r', encoding="utf8")
    token = file.read()
    if(len(token) == 0): # if no text was converted
        print('****************************Warning, token file is empty')
    file.close()
    # print(token)
    return token

def getInputFile():
    root = tk.Tk()
    root.withdraw()
    file = fd.askopenfile(initialdir = r'H:\Documents', filetypes = (("CSV files","*.csv"),("all files","*.*")))
    print(file.name)
    return file.name

# start program
csv_path = ""
log_path = 'H:\\Documents\\Projects\\ScratchPad\\logs\\'
time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
rowCntr = 0
emails = []

if(csv_path == ""):
    csv_path = getInputFile()
    if(csv_path == "" or csv_path is None):
        print("no csv, quitting")
        sys.exit(0)
try:        
    log_path = log_path + "LeadDeleteByEmail_" + time + ".txt"
    logfile = open(log_path, 'w+')
    logfile.write("Log created at " + time + "\n")
    logfile.write("this action is being ran by " + os.getlogin() 
                   + " on computer " + os.environ['COMPUTERNAME']+ '\n')
        
    logfile.write("Loading input CSV from " + csv_path + "\n")
    
    logfile.write("Done loading input \n")
    csvOut = open(csv_path.replace(".csv","") + '-IDs.csv', 'w+')
    csvOut.write("foundID, email\n")
    logfile.write("Done Opening output file" + csv_path.replace(".csv","") + '-IDs.csv'+ " \n")
except:
    print("Unexpected error:", sys.exc_info()[0])
    sys.exit(-1)
    
with open(csv_path, encoding="utf8", newline='', errors='ignore') as csvIn:
    reader = csv.reader(csvIn, delimiter=',')
    logfile.write("Opened CSV in at " + csv_path + "\n")
    print("opened " + csv_path)
    
    for row in reader:
        rowCntr += 1 # skip first row
        
        if not row:
            continue
        try:
            tempID = str(row[0])
            print(tempID)
            emails.append(tempID) #add the id from the CSV to the list
            logfile.write(tempID + "\n")
            
        except ValueError:
            file.write("ERROR: " + str(row[0]) + " is not a valid number and ID\n")
            print("ERROR: " + str(row[0]) + " is not a valid number and ID\n")

client = basecrm.Client(access_token = getToken()) # creates the baseCRM interface service
       
for tEmail in emails:
    results = client.leads.list(email=tEmail) # fetch leads with the current email into a list
    if(len(results) != 0):
        logfile.write("found matching IDs " + str(len(results)) + "\n") #go through results list
        for result in results:
            
            temp = client.leads.destroy(result['id']) #returns bool on delete success
            if(temp == True): # if good, log it.
                logfile.write("deleting " + str(result['id']) + "\n")
                csvOut.write(str(result['id']) + "," + tEmail)                
            else: # no real error handling here
                logfile.write("Could not delete " + str(result['id']) + "\n")
    else:
        logfile.write("no leads located for " + tEmail + "\n")
time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
logfile.write("done at " + time)
        