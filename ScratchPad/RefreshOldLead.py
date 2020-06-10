'''
Created on Jan 20, 2017

@author: jchavis

This module will take a CSV list of Base IDs for Leads, download the lead
    data, delete the lead the from Base, and re-import the lead into base

@attention: Set to clear all tags and reapply OTJT and M/H as needed
@attention: Sets new lead type to B-Lead or TDS-B lead based on old data

full command line support, use -h or --help for options.
    -o or --owner - name of the owner "Bob Saget"
    -f or --file - path to file, defaults to empty ie "c:\apps\myfile.csv"
    -l or --logdir - path to write the log file to, defaults to 
        "[currentdir]\logs\"
    -w or --wait - no means the program closes when done, anything else
        means it waits for user input

List of future updates (prefix out for tracking) 
@todo:DONE 2-14-2017 add proper input checking for numeric, etc
@todo:     exception handling on all reads
@todo:Done add command line arguments to set veriables 
@todo:Done option to hold open console on compltion.
@todo:Done option to skip GUI 
@todo:     exception handling on all request calls
@todo:     convert simple text dump of json to CSV export?
@todo:Done look into resource cleanup of file and reader.
@todo:     remove redundant token searching paths
@todo:Done add custom log file pathing
@todo:     add log copy to shared log repository

2/1/2017 - started
2/13/2017 - Finished core functionality with minimum error checking, no
    correction, no note transfer
12/12/2017 - resturctured main logic into startProg function, changed
    owner and source fetching
'''

import datetime  # for comparing time stamps
import os, ctypes, sys
import requests, json
import csv
import argparse
import tkinter.filedialog as fd  # for picking the file
import tkinter
#import grequests # can't use because of dependency failing

owners = {}
sources = {}

#take care of our command line arguments
 # build parser
parser = argparse.ArgumentParser(description='Handle commandline options')
parser.add_argument('--owner','-o', dest='owner', \
                    help="Optional owner flag", required=False) #owner arg
# CSV file argument
parser.add_argument('--file', '-f', dest='file', \
                    help="file CSV to process", required=False) 
# log file directory
parser.add_argument('--logdir', '-l', dest='logdir', \
                    help="directory to store logs in", required=False) 
parser.add_argument('--wait', '-w', dest='wait', \
                    help="No means the program closes after running, " +\
                    "else, it waits for key", required=False) # wait arg

# fetch args into namespace so we can call args.argName
args = parser.parse_args() 


def getSource(sourceName):
    """serves as a getter for source that reads sources by the key and 
        returns value
    all performs blank, space, and null check (returns empty)
    if sources not loaded, it will load them via api
    """
    global sources
    if not sources or len(sources) == 0:
        loadSources()
        
    if(sourceName == "" or sourceName == " " or sourceName is None):
        return ""
    else:
        return sources[sourceName]


def loadSources():
    """fetches the inital sources list from the baseAPI. This will only 
        load the first 100
    currently set to use global, could comment it out and simple return 
        source for sources = loadSources()
    use as loadSources() with the sources loaded into global sources 
        variable as dict
    """
    global token
    if token is None or token == '':
        token = getToken()
    
    sheaders = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token}
    
    sURL = "https://api.getbase.com/v2/lead_sources?per_page=100"
    sresponse = requests.get(url=sURL, headers=sheaders, verify=True)#send
    sresponse_json = json.loads(sresponse.text) #read in the response JSON
    items = sresponse_json['items']
    global sources
    sources = {}
    for item in items:
        sources[item['data']['name']] = item['data']['id']
        

def setPath():
    """this function is called by the CSV path button to set the logPath
        variable"""
    global csv_path, master
    FILEOPENOPTIONS = dict(defaultextension='.csv', \
                           filetypes=[('CSV file', '*.csv'), \
                                      ('All files', '*.*')])#options
    csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    csv_text.set(csv_path)
    errorMsg.set("") #clear and user error message and proper path loading
    return # go back

def setLog():
    """this function is called when the user clicks the button to change 
        log path"""
    global logPath, master, l2
    #defPath = r'//NAS3/Users/' + os.getlogin() + r'/Documents' 
    # currently not working
    #tempPath = fd.askdirectory(parent=master, initaldir=defPath)
    tempPath = tkinter.filedialog.askdirectory() # open dialog to pick
    #the directory
    logPath.set(tempPath) # update the StringVar so user see's new path
    errorMsg.set("") # reset user's error message as needed
    return # go back

def loadOwners():
    """loads a dict of available owners in the following format 
        {"James Chavis" : 123456789}
    loads into owners
    """
    global token
    global owners
    if token is None or token == '':
        token = getToken()
    
    oheaders = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token}
    
    oURL = 'https://api.getbase.com/v2/users?per_page=100&status=active'
    oresponse = requests.get(url=oURL, headers=oheaders, verify = True)
    oresponse_json = json.loads(oresponse.text) #read in the response JSON
    items = oresponse_json['items']
    owners = {}
    
    for item in items:
        owners[item['data']['name']] = item['data']['id']

def getOwner(ownerName):
    """this function finds the owner id for the given name and returns
        owner_id as an int"""
    global owners
    if not owners or len(owners) == 0:
        loadOwners()
    
    if(ownerName == "" or ownerName == " " or ownerName is None):
        return ""
    else:
        return owners[ownerName] 


def today():
    """returns todays date in the standard Yyyy-mm-dd format"""
    today = datetime.datetime.now()
    #return today.strftime('%Y-%m-%d')
    return today.strftime('%m/%d/%Y')


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

#--------------------------------------------------------START PROGRAM ---
def startProgram():
    """Main logic of the program"""
    # redundant check
    if(csv_path is None or csv_path == ""): #if the file picker is closed
        exit("No file chosen")  # shutdown before log is written
        
    ownerID = getOwner(ownerVar.get()) #record new owner ID num
    
    # open log
    # get timestamp for the log writing.
    time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')  
    
    #problem with paths not ending in \ sometimes, lets hack around it
    pathList = list(logPath.get())
    if pathList[len(pathList)-1] !='\\' or\
       pathList[len(pathList)-1] != '/':
        
        if '\\' in pathList:
            logPath.set(logPath.get() + '\\')
        else:
            logPath.set(logPath.get() + '/')
    
    # create and open the log file for this session
    file = open(logPath.get() + 'Refresh-Lead-' + time + '.txt', 'w+')  
    print("making log file " + logPath.get() + 'Refresh-Lead-' 
          + time + '.txt')
    file.write('this log was written to ' + logPath.get() 
               + 'Refresh-Lead-' + time + '.txt\n')
    file.write("starting leads update at " + time + '\n')  # write to log
    file.write("using CSV: " + csv_path + '\n')
    file.write("owner is set to " + ownerVar.get()+ '\n')
    file.write("log path set to " + logPath.get()+ '\n')
    file.write("this action is being ran by " + os.getlogin() 
               + " on computer " + os.environ['COMPUTERNAME']+ '\n')
    file.write("command line args: " + str(args) + "\n")
    
    #lets make a csv file to track oldIDs to newIDs easily
    csvOut = open(logPath.get()+'Refresh-Lead-' + time + '-IDs.csv', 'w+')
    csvOut.write("oldIDs, newIDs\n") # header
    
    oldBaseIDs = [] # this will hold the id's of Leads
    failed = 0 # track failures
    passed = 0 # track success
    
    # Now we open the CSV containing the id's of the leads we are going
    #    to work with
    # The CSV should look something like below, read from column 0:
    # |   id   |
    # | 123654 |
    # | 446588 |
    with open(csv_path, encoding="utf8", newline='',
              errors='ignore') as csvfile:  # open file as UTF-8
        # makes the file a csv reader
        reader = csv.reader(csvfile, delimiter=',')
        rowCntr = -1 #start index, will track which row the process is on
        
        for row in reader: #reader contains all our records
            rowCntr += 1 #increment our tracker, row0 is the header row
            if(rowCntr == 0): #skip the header row
                continue # skip
            # if the row is empty (usually on the last row), skip ahead
            if not row: 
                continue
            
            #if not header, lets take a look at the data
            #check to see if the data is numeric
            try:
                tempID = int(row[0])
                oldBaseIDs.append(tempID) #add the id from the CSV to the list
            except ValueError:
                file.write("ERROR: " + str(row[0]) + " is not a valid number and ID\n")
                print("ERROR: " + str(row[0]) + " is not a valid number and ID\n")
                failed += 1
                
    #done reading in the IDs
    file.write("loaded " + str(len(oldBaseIDs)) + " IDs from the CSV file\n")
    file.write(json.dumps(oldBaseIDs, sort_keys=True, indent=4))
    file.write("\n\n")
    print("loaded " + str(len(oldBaseIDs)) + " IDs from the CSV file\n")
    
    #start the online stuff
    #the starting URL for getting results
    url = "https://api.getbase.com/v2/leads/"
    headers = { # headers for the HTTP calls
        'accept':"application/json",
        'authorization' : "Bearer " + token,
        'content-type': "application/json"
        }
    
    noteParams = {"per_page" : 100, "page" : 1, }
    
    rowCntr = 0 # reset the counter to zero to track num of IDs
    oldLeads = [] # this will hold the response json for all the leads loaded into
    
    #step rough all the loaded IDs
    for currID in oldBaseIDs:
            print("starting with old ID " + str(oldBaseIDs[rowCntr]) + "\n")
            file.write("starting with old ID " + str(oldBaseIDs[rowCntr]) + "\n")
            
            currURL = url + str(oldBaseIDs[rowCntr])  # append the id to the API url
            
            response = requests.request("GET", currURL, headers=headers) # make the call
            
            # check status code for error, this is most likely a 404 status code because the lead cannot be found
            if response.status_code != 200: # 200 is the good code
                print("something went wrong getting data, got status code " + str(response.status_code)) # error message
                file.write("something went wrong getting data, got status code " + str(response.status_code) + " skipping to the next ID\n")
                failed += 1
                rowCntr += 1 # ready to move to the next row
                continue # continue to the next ID once the error has been noted.    
            
            file.write("found " + str(oldBaseIDs[rowCntr]) + ", deleting the lead\n") 
            data = json.loads(response.text) # make a json
            file.write(json.dumps(data, sort_keys=True, indent=4)) # write the json to log for safe keeping
    
            # now we can change the info, and push it back to base as a B lead
            data['data']['owner_id'] = ownerID # set the owner to choosen ID
            
#NEW LEAD TYPE GOES HERE!!!!!!!!!!!!!!!!
            #data['data']['custom_fields']['New Lead Type'] = "TDS-B Lead" # change the lead type to B type
            data['data']['custom_fields']['New Lead Type'] = "A Lead" 
            
#             if('New Lead Type' in data['data']['custom_fields'] \
#                and data['data']['custom_fields']['New Lead Type'] != None and \
#                "TDS" in data['data']['custom_fields']['New Lead Type']):
#                 data['data']['custom_fields']['New Lead Type'] = "TDS-B Lead"
#             else:
#                 data['data']['custom_fields']['New Lead Type'] = "B Lead"
            
            data['data']['custom_fields']['StatusChange'] = today() # mark today as the date of the change to a B lead
            
    #CHANGE STATUS TO INCOMMING
            data['data']['status'] = "Incoming"
            
    
    
            # delete fields that aren't used on create
            del data['meta'] # metadata about the lead
            del data['data']['id'] # a new id will be assigned
            del data['data']['created_at'] # create and update dates are not needed
            del data['data']['updated_at']
            del data['data']['creator_id']
            
            #refresh tags, only add M/H Phone if mobile or home is populated
            del data['data']['tags']
            tagList = []
            
            if 'mobile' in data['data'] and data['data']['mobile'] is not None:
                tagList.append('M/H Phone')
            elif 'Home Phone' in data['data']['custom_fields'] and data['data']['custom_fields'] is not None:
                tagList.append('M/H Phone')
            
            tagList.append('OTJT');
            data['data']['tags'] = tagList
            
            #END REFRESH TAGS
            
            #ENSURE TDS IS YES
            data['data']['custom_fields']['TDS'] = 'Yes'
            
            if "unqualified_reason_id" in data['data']:
                del data['data']['unqualified_reason_id']
            
            # let's delete the lead
            response = requests.request('DELETE', url=currURL, headers=headers)
            
            # check status code for error, this should be code 204
            if response.status_code != 204: # 204 is the good code for no data found
                print("something went wrong deleting, got status code " + str(response.status_code)) # error message
                file.write("something went wrong deleting, got status code " + str(response.status_code) + " skipping to the next ID\n")
                failed += 1
                rowCntr += 1 # ready to move to the next row
                continue # continue to the next ID once the error has been noted.
            
            # Now that the data has changed, let us go ahead and POST (create) a new lead but NOT upserting (avoid merge)
            response = requests.post(url='https://api.getbase.com/v2/leads', headers=headers, data=json.dumps(data), verify=True)
            
            # check for errors and notify if needed
            if response.status_code != 200:
                print("something went wrong creating a lead, got status code " + str(response.status_code) + '\n')
                file.write("something went wrong creating a lead, got status code " + str(response.status_code)+ '\n')
                file.write(json.dumps(data))
                failed += 1
                rowCntr += 1 # ready to move to the next row
                print(json.dumps(data))
                continue
            
            #if we reach this point, everything is good to go
            file.write("\nDumping new Lead Data\n")
            data = json.loads(response.text)
            file.write(json.dumps(data, sort_keys=True, indent=4))
            file.write("\nOld Base ID: " + str(oldBaseIDs[rowCntr]) + "\tnew Base ID: " + str(data['data']['id']) + "\n")
            csvOut.write(str(oldBaseIDs[rowCntr]) + ", " + str(data['data']['id']) + "\n")
            print("Old Base ID: " + str(oldBaseIDs[rowCntr]) + ",\tnew Base ID: " + str(data['data']['id']) + "\n")
            
            file.write("\nDone with lead" + str(rowCntr) + "-------------------------------------------------------\n\n\n")
            rowCntr += 1 # ready to move to the next row
            passed += 1
            
            errorMsg.set("Working..." + "{0:.2f}".format((passed + failed)/ len(oldBaseIDs)) + "% Done" )
            
    print("Passed: " + str(passed) + '\n')
    print("failed: " + str(failed) + '\n')
    print("Closing ---------------------------------------- Goodbye!")
    file.write("Passed: " + str(passed) + '\n')
    file.write("failed: " + str(failed) + '\n')
    file.write('done at ' + datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    file.close()
    csvOut.close()
    errorMsg.set("finished with " + str(passed) + " passed and " + str(failed) + " fails")
    if args.wait == 'no':
        input('Press enter to continue')
    #end main logic of startProg()
'''
-initalization code here
'''
#load the token
token = getToken()
skipGUI = (args.owner != None and args.owner != "" and args.file != None and args.file != "")

#Start the GUI stuff to get pathing and new lead owner
master = tkinter.Tk() #  set root window
if skipGUI == True:
    master.withdraw()
iconPath = r'\\nas3\Shared\RALIM\logos\base-crm16and64.ico' # path to ICON

logPath = tkinter.StringVar(master) # default path to the log
logPath.set( 'h:\\logs\\' ) # get current path
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


# this may be redundant, used on tkinter's option menu
# maybe replace with *(owners.keys())
# how do you dereference a returned dict in python
loadOwners()
loadSources()
newOwnerList = owners.keys() 

master.title("Enter owner's full name") # pretty title
master.iconbitmap(iconPath) # set icon
master.iconbitmap(default=iconPath) # set it again.

ownerVar = tkinter.StringVar(master) # holds the new lead owner
ownerVar.set("James Chavis") # default owner to James Chavis
if args.owner != None and args.owner != '':
    ownerVar.set(args.owner)
    print('owner set to ' + ownerVar.get())
    
# this condition means both are given in command line and there is no reason to use the GUI
if skipGUI == True: # this condition means both are given in command line
    master.quit()
    print("skipping GUI, command args given: " + str(args) )
else:
    # lets build the labels 
    l1 = tkinter.Label(master, text="Enter name of new owner").grid(row=1, column=1, sticky=tkinter.W, pady=4, padx=4) # add a label for the owner box
    l2 = tkinter.Label(master, textvariable=logPath).grid(row=2, column=1, sticky=tkinter.W, pady=4, padx=4) # label for the log path
    l3 = tkinter.Label(master, textvariable=csv_text).grid(row=0, column=1, sticky=tkinter.W, pady=4, padx=4) # csv file path label
    errorLabel = tkinter.Label(master, textvariable=errorMsg, fg="red", font = "Helvetica 12 bold italic", width=20) \
        .grid(row=4, sticky=tkinter.W, pady=4, padx=4) # error message label
    
    # lets build the objects
    o1 = tkinter.OptionMenu(master, ownerVar, *newOwnerList).grid(row=1, column=0, sticky="ew", pady=4, padx=4)  # drop down list of owners, note list pointer
    b1 = tkinter.Button(master, text="Run the Program", font="Helvetica 12 bold italic", command=startProgram, width=20).grid(row=3, column=0,sticky="ew", pady=4, padx=4) # add a single button to the popup
    b2 = tkinter.Button(master, text="Choose CSV File", command=setPath, width=20).grid(row=0, column=0, sticky="ew", pady=4, padx=4) # use to pick the buttom
    b3 = tkinter.Button(master, text="Change Log Path", command=setLog, width=20).grid(row=2, column=0, sticky="ew", pady=4, padx=4) # used to change the default log path
    exitBtn = tkinter.Button(master, text="Close", font="Helvetica 12 bold italic", command=master.quit, width=20).grid(row=3, column=1, sticky="ew", pady=4, padx=4) # quits the program
    #start the GUI
    tkinter.mainloop() # start the window thread


        