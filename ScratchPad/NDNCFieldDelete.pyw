'''
Created on 11/15/2017

@author: jchavis

This module will take a CSV list of Base IDs for leads and remove all NDNC fields.

full command line support, use -h or --help for options.
    -o or --owner - name of the owner "Bob Saget"
    -f or --file - path to file, defaults to empty ie "c:\apps\myfile.csv"
    -l or --logdir - path to write the log file to, defaults to "[currentdir]\logs\"
    -w or --wait - no means the program closes when done, anything else means it waits for user input

List of future updates (prefix out for tracking) 
@todo:DONE 2-14-2017 add proper input checking for numeric, etc
@todo: exception handling on all reads
@todo:Done add command line arguments to set variables 
@todo:Done option to hold open console on c.
@todo:Done option to skip GUI 
@todo: exception handling on all request calls
@todo: Seriously, get grequests for multithreading working.
@todo: convert simple text dump of json to CSV export?
@todo:Done look into resource cleanup of file and reader.
@todo: remove redundant token searching paths
@todo:Done add custom log file pathing
@todo: add log copy to shared log repository

'''

import datetime  # for comparing timestamps
import os, ctypes, sys
import requests, json
import csv
import argparse
import tkinter.filedialog as fd  # for picking the file
import tkinter
#import grequests # can't use because of dependency failing

owners = {} #loaded at start from csv during the GUI build

#take care of our command line arguments
parser = argparse.ArgumentParser(description='Handle commandline options') # build parser
parser.add_argument('--owner','-o', dest='owner', help="Optional owner flag", required=False) # owner arg
parser.add_argument('--file', '-f', dest='file', help="file CSV to process", required=False) # CSV file argument
parser.add_argument('--logdir', '-l', dest='logdir', help="directory to store logs in", required=False) # log file directory
parser.add_argument('--wait', '-w', dest='wait', help="No means the program closes after running, else, it waits for key", required=False) # wait arg
args = parser.parse_args() # fetch args into namespace so we can call args.argName

def loadOwners():
    global token
    global owners
    if token is None or token == '':
        token = getToken()
    
    oheaders = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token}
    
    oURL = 'https://api.getbase.com/v2/users?per_page=100&status=active'
    oresponse = requests.get(url=oURL, headers=oheaders, verify = True)
    oresponse_json = json.loads(oresponse.text)  # read in the response JSON
    items = oresponse_json['items']
    owners = {}
    
    for item in items:
        owners[item['data']['name']] = item['data']['id']

# this function finds the owner id for the given name and returns owner_id as an int
def getOwner(ownerName):
    global owners
    if not owners or len(owners) == 0:
        loadOwners()
    
    if(ownerName == "" or ownerName == " " or ownerName is None):
        return ""
    else:
        return owners[ownerName] 

def setPath():
    """this function is called by the CSV path button to set the logPath variable"""
    global csv_path, master
    FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])#options
    csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    csv_text.set(csv_path)
    errorMsg.set("") # clear and user error message and proper path loading
    return # go back


#@todo: Fix the initial directory picker path to  \\nas3\users\ + os.getlogin() + \Documents\

def setLog():
    """this function is called when the user clicks the button to change log path"""
    global logPath, master, l2
    #defPath = r'//NAS3/Users/' + os.getlogin() + r'/Documents' # currently not working
    #tempPath = fd.askdirectory(parent=master, initaldir=defPath)
    tempPath = tkinter.filedialog.askdirectory() # open dialog to pick the directory
    logPath.set(tempPath) # update the StringVar so user see's new path
    errorMsg.set("") # reset user's error message as needed
    return # go back


def getOwner(name):
    global owners
    if len(owners) == 0:
        loadOwners()
        #print(owners)
        
    if isinstance(name, int):
        for k,v in owners.items():
            if v == name:
                return k
    else :
        return owners[name]


def today():
    """returns todays date in the standard Yyyy-mm-dd format"""
    today = datetime.datetime.now()
    #return today.strftime('%Y-%m-%d')
    return today.strftime('%m/%d/%Y')


def getToken():
    """this method will attempt to find a file containing the API token"""
    path = ""
    if(os.path.isfile("C:\\Apps\\NiceOffice\\token")): # search the C:\Apps folder
        path = "C:\\Apps\\NiceOffice\\token" # Found it! Load it
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token")): # search the network shared NOE folder
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token"
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token")): # search the OTHER network NOE location
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token"
    else: # if the token is not found in another location, ask the user to find it
        ctypes.windll.user32.MessageBoxW(0, "A token file was not found in your NOE folder, please choose the token file", "Token File", 0)
        FILEOPENOPTIONS = dict(filetypes=[('TOKEN file', '*.*')], title=['Choose token file'])
        root = tkinter.Tk()  # where to open
        root.withdraw()
        # withdraw()  # hide Frame
        path = tkinter.filedialog.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    if(path == ""): # if not path was chosen, quit
        ctypes.windll.user32.MessageBoxW(0, "No file was chosen, quiting", "Token File", 0)
        exit()
    
    # read in the token from the file and return the token as a string
    file = open(path, 'r', encoding="utf8")
    token = file.read()
    if(len(token) == 0): # if no text was converted
        print('******************************Warning, token file is empty')
    file.close()
    # print(token)
    return token

#--------------------------------------------------------START PROGRAM ---------------------------------------------------------------------#

#load the token
token = getToken()
skipGUI = (args.owner != None and args.owner != "" and args.file != None and args.file != "")

#Start the GUI stuff to get pathing and new lead owner
master = tkinter.Tk() #  set root window
if skipGUI == True:
    master.withdraw()
iconPath = r'S:\logos\base-crm16and64.ico' # path to ICON

logPath = tkinter.StringVar(master) # default path to the log
logPath.set(os.path.dirname(__file__) + '\\logs\\' ) # get current path
if args.logdir != None and args.logdir != "":
    logPath.set(args.logdir.replace('"','\\'))
    print('log path set to ' + logPath.get())

csv_text = tkinter.StringVar(master)
csv_text.set("<----- choose input file")
csv_path = "" # empty file path
if args.file != None and args.file != "":
    csv_path = args.file
    csv_text.set(csv_path)
    print('csv path set to ' + csv_path)
    
errorMsg = tkinter.StringVar(master) # make a message for the error label
errorMsg.set("") #  set error message blank until there is an actual error


    
master.title("Contact to Lead") # pretty title
master.iconbitmap(iconPath) # set icon
master.iconbitmap(default=iconPath) # set it again.

#ownerVar = tkinter.StringVar(master) # holds the new lead owner
#ownerVar.set("James Chavis") # default owner to James Chavis
# if args.owner != None and args.owner != '':
#     ownerVar.set(args.owner)
#     print('owner set to ' + ownerVar.get())
    
# this condition means both are given in command line and there is no reason to use the GUI
if skipGUI == True: # this condition means both are given in command line
    master.quit()
    print("skipping GUI, command args given: " + str(args) )
else:
    # lets build the labels 
    #l1 = tkinter.Label(master, text="Enter name of new owner").grid(row=1, column=1, sticky=tkinter.W, pady=4, padx=4) # add a label for the owner box
    l2 = tkinter.Label(master, textvariable=logPath).grid(row=2, column=1, sticky=tkinter.W, pady=4, padx=4) # label for the log path
    l3 = tkinter.Label(master, textvariable=csv_text).grid(row=0, column=1, sticky=tkinter.W, pady=4, padx=4) # csv file path label
    errorLabel = tkinter.Label(master, textvariable=errorMsg, fg="red", font = "Helvetica 12 bold italic", width=40) \
        .grid(row=4, sticky=tkinter.W, pady=4, padx=4) # error message label
    
    # lets build the objects
    #o1 = tkinter.OptionMenu(master, ownerVar, *newOwnerList).grid(row=1, column=0, sticky="ew", pady=4, padx=4)  # drop down list of owners, note list pointer
    b1 = tkinter.Button(master, text="Run the Program", font="Helvetica 12 bold italic", command=getOwner, width=20).grid(row=3, column=0,sticky="ew", pady=4, padx=4) # add a single button to the popup
    b2 = tkinter.Button(master, text="Choose CSV File", command=setPath, width=20).grid(row=0, column=0, sticky="ew", pady=4, padx=4) # use to pick the buttom
    b3 = tkinter.Button(master, text="Change Log Path", command=setLog, width=20).grid(row=2, column=0, sticky="ew", pady=4, padx=4) # used to change the default log path
    exitBtn = tkinter.Button(master, text="Close", font="Helvetica 12 bold italic", command=master.quit, width=20).grid(row=3, column=1, sticky="ew", pady=4, padx=4) # quits the program
    #start the GUI
    tkinter.mainloop() # start the window thread

# redundant check
if(csv_path is None or csv_path == ""):  # if the file picker is closed
    exit("No file chosen")  # shutdown before log is written

# open log
time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.

#weird problem with paths not ending in \ sometimes, lets hack around it
pathList = list(logPath.get())
if pathList[len(pathList)-1] != '\\' or pathList[len(pathList)-1] != '/':
    if '\\' in pathList:
        logPath.set(logPath.get() + '\\')
    else:
        logPath.set(logPath.get() + '/')

file = open(logPath.get() + 'NDNCFieldDelete-' + time + '.txt', 'w+')  # create and open the log file for this session
print("making log file " + logPath.get() + '90DayLostDealToLead-' + time + '.txt')
file.write('this log was written to ' + logPath.get() + '90DayLostDealToLead' + time + '.txt\n')
file.write("starting update at " + time + '\n')  # write to log
file.write("using CSV: " + csv_path + '\n')
#file.write("owner is set to " + ownerVar.get()+ '\n')
file.write("log path set to " + logPath.get()+ '\n')
file.write("this action is being ran by " + os.getlogin() + " on computer " + os.environ['COMPUTERNAME']+ '\n')
file.write("command line args: " + str(args) + "\n")


oldBaseIDs = [] # this will hold the id's of the A or TDS A Contacts (probably, maybe)
failed = 0 # track failures
passed = 0 # track success

# Now we open the CSV containing the id's of the contacts we are going to work with
# The CSV should look something like below, read from column 0:
# |   id   |
# | 123654 |
# | 446588 |
with open(csv_path, encoding="utf8", newline='', errors='ignore') as csvfile:  # open file as UTF-8
    reader = csv.reader(csvfile, delimiter=',')  # makes the file a csv reader
    rowCntr = -1  # start index, will track which row the process is on
    
    for row in reader: #reader contains all our records
        rowCntr += 1 #increment our tracker, row0 is the header row
        if(rowCntr == 0): #skip the header row
            continue # skip
        
        if not row: # if the row is empty (usually on the last row), skip ahead
            continue
        
        #if not header, lets take a look at the data
        #check to see if the data is numeric
        try: # if int conversion fails, this isn't a base ID
            tempID = int(row[0])
            oldBaseIDs.append(tempID) #add the id from the CSV to the list
        except ValueError:
            file.write("ERROR: " + str(row[0]) + " is not a valid number and ID\n")
            print("ERROR: " + str(row[0]) + " is not a valid number and ID\n")
            failed += 1 # adding failure here since the number won't be added to the oldBaseIDs list
            
#done reading in the IDs
file.write("loaded " + str(len(oldBaseIDs)) + " IDs from the CSV file\n")
file.write(json.dumps(oldBaseIDs, sort_keys=True, indent=4))
file.write("\n\n")
print("loaded " + str(len(oldBaseIDs)) + " IDs from the CSV file\n")

#start the online stuff
#the starting URL for getting results
url = "https://api.getbase.com/v2/contacts/"
headers = { # headers for the HTTP calls
    'accept':"application/json",
    'authorization' : "Bearer " + token,
    'content-type': "application/json"
    }

#noteParams = {"per_page" : 100, "page" : 1, }

rowCntr = 0 # reset the counter to zero to track num of IDs
#oldContacts = [] # this will hold the response json for all the leads loaded into
finished = 0
#step rough all the loaded IDs
for currID in oldBaseIDs:
        print("starting with old ID " + str(oldBaseIDs[rowCntr]) + "\n")
        file.write("starting with old ID " + str(oldBaseIDs[rowCntr]) + "\n")
        
        currURL = url + str(oldBaseIDs[rowCntr])  # append the id to the API url
        
        payload = {}
        payload['data'] = {}
        custFields = {}
        custFields['NDNC'] = ""
        custFields['NDNC ExpDate'] = ""
        custFields['NDNC HmPhone'] = ""
        custFields['Ndnc hm phone #1'] = ""
        custFields['Ndnc exp date #1'] = ""
        custFields['NDNC HmPhone Status'] = ""
        custFields['Alt Phone NDNC'] = ""
        custFields['Alt Phone NDNC Exp Date'] = ""
        custFields['Alt phone #1 NDNC'] = ""
        custFields['Alt phone #1 NDNC Exp Date'] = ""
        custFields['Alt phone #2 NDNC'] = ""
        custFields['Alt phone #2 NDNC Exp Date'] = ""
        custFields['Alt Phone #3 NDNC'] = ""
        custFields['Alt Phone #3 NDNC Exp Date'] = ""
        custFields['Alt Phone #4 NDNC'] = ""
        custFields['Alt Phone #4 NDNC Exp Date'] = ""
        custFields['Alt Phone #5 NDNC'] = ""
        custFields['Alt Phone #5 NDNC Exp Date'] = ""
        custFields['Alt Phone #6 NDNC Exp Date'] = ""
        custFields['Alt Phone #7 NDNC'] = ""
        custFields['Alt Phone #7 NDNC Exp Date'] = ""
        custFields['Alt Phone #6 NDNC'] = ""
        payload['data']['custom_fields'] = custFields
        
        response = requests.put(url=url, headers=headers,data=json.dumps(payload), verify=True)
        
        # check status code for error, this is most likely a 404 status code because the contact cannot be found
        if response.status_code != 200: # 200 is the good code
            print("something went wrong getting data, got status code " + str(response.status_code)) # error message
            file.write("something went wrong getting data, got status code " + str(response.status_code) + " skipping to the next ID\n")
            failed += 1
            rowCntr += 1 # ready to move to the next row
            finished +=1
            continue # continue to the next ID once the error has been noted.

        file.write("found " + str(oldBaseIDs[rowCntr]) + ", moving to notes and deals...\n") 
        data = json.loads(response.text) # make a json
        file.write(json.dumps(data, sort_keys=True, indent=4)) # write the json to log for safe keeping
        file.write('\n')
        #print(json.dumps(data, sort_keys=True, indent=4))         
        
        file.write("\nDone with lead-------------------------------------------------------\n\n\n")
        rowCntr += 1 # ready to move to the next row
        passed += 1
        
        finished += 1 
        if passed != 0:
            m, s = divmod(((len(oldBaseIDs) - finished)*3), 60)
            h, m = divmod(m, 60)
            remaining = ("%02d:%02d:%02d" % (h, m, s))
            errorMsg.set("Working:" + "{0:.2f}".format((finished/ len(oldBaseIDs))*100) + "% Done, Remaining(h:m:s): " + remaining)
            master.update()
            print("Working:" + "{0:.2f}".format((finished/ len(oldBaseIDs))*100) + "% Done, Remaining(h:m:s): " + remaining)
            print('\nDone with lead ' + str(currID) + '--------------------------------------------------------\n\n' )
        
print("Passed: " + str(passed) + '\n')
print("failed: " + str(failed) + '\n')
print("Closing ---------------------------------------- Goodbye!")
file.write("Passed: " + str(passed) + '\n')
file.write("failed: " + str(failed) + '\n')
file.write('done at ' + datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
file.close()
errorMsg.set("finished with " + str(passed) + " passed and " + str(failed) + " fails")
#if args.wait != 'no':
#    input('Press enter to continue')
        