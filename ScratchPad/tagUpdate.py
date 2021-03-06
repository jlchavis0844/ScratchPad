'''
Created on Dec 22, 2016
This module will add, not replace, the users tags
The module will read in a CSV info in the following order:
    Type : contacts or Leads **must be plural
    id : Base ID for lead or contact
    tag0: The first tag to add
    ...
    tagN: The last tag to add

12-23-2016 - scratch the unirest idea, switch to requests
12-27-2016 - continued development on the request and more
12-27-2016 - completed by adding some error correction, duplicate detection, and exception handling
@author: jchavis
'''

import os, tkinter, ctypes, csv, json, requests
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime

#This function will check for a text file called token which holds the Base API Token in plain text
# this token will be loaded, read, and stored as the token variable that is returned
# the function will read this computer's name and then check the network shared drive locations
#     \\NAME\now\token
#     \\NAME\Noe
# If the file is not located, a file picker will be loaded for the user to find the token file.
def getToken():
    path = ""
    if(os.path.isfile("C:\\Apps\\NiceOffice\\token")):
        path = "C:\\Apps\\NiceOffice\\token"
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token")):
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token"
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token")):
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token"
    else:
        ctypes.windll.user32.MessageBoxW(0, "A token file was not found in your NOE folder, please choose the token file", "Token File", 0)
        FILEOPENOPTIONS = dict(filetypes=[('TOKEN file', '*.*')], title=['Choose token file'])
        root = tkinter.Tk()  # where to open
        root.withdraw()
        # withdraw()  # hide Frame
        path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    if(path == ""):
        ctypes.windll.user32.MessageBoxW(0, "No file was chosen, quiting", "Token File", 0)
        exit()
    
    file = open(path, 'r', encoding="utf8")
    token = file.read()
    file.close()
    # print(token)
    return token

def writeAndQuit(response, log):
    log.write(response.text)
    print('ERROR: received status code: ' + str(response.status_code) + '\n')
    #log.close()
    #exit(response.status_code)
    
#case insensitive check of all the current api tags with the current tag. If match is found, true, false otherwise
def duplicateTagCheck(APItags, currTag):
    for x in range(len(APItags)):
        if(APItags[x].lower() == currTag.lower()):
            return True
    return False

# need callback function for Async Unirest calls
#def callBack_function(response):
#    print('Empty function, response code was ' + response.code)
    
    
# Setup for the file picker
FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get time stamp for the log writing.
#path = os.path.dirname(__file__)  # get current path
path = 'H:\\'
# load in the API token, for security, the token is saved as plain text locally in the NOE folder
token = getToken()

# get input file
root = tkinter.Tk()  # where to open
root.withdraw()  # hide Frame
csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file

if(csv_path is None or csv_path == ""):  # if the file picker is closed
    exit("No file chosen")  # shutdown before log is written

file = open(path + '\\logs\\tagUpdate' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("starting tag update at " + time + '\n')  # write to log
file.write("using CSV: " + csv_path + '\n')
rowCntr = -1

# start API call setup, let us try Async calls with unirest libs
headers = {'Accept': 'application/json',
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + token}

baseURL = 'https://api.getbase.com/v2/'

with open(csv_path, encoding="utf8", newline='', errors = 'ignore') as csvfile: # open files as UTF-8
    reader = csv.reader(csvfile, delimiter=',')
    
    print('------------------------------------------------ Here we go ------------------------------------------------')
    
    for row in reader:  # iterate through each row (record)
        rowCntr += 1  # start at zero
        if(rowCntr == 0):  # skip row 0, we don't need the header names
            continue;  # goes to top of the loop
        
        #Let's start each row by loading in their current tags from the internet
        url = (baseURL + row[0] + '/' +  row[1]).lower()
        #response = unirest.get(url, headers = headers, params = "",  callback = callBack_function) # send it
        response = requests.get(url=url, headers=headers, data="", verify=True)
        
        #something bad happened, lets give up
        if(response.status_code != 200):
            writeAndQuit(response, file)
            continue
        response_json = json.loads(response.text) # make a json of the response
        APItags = str(response_json['data']['tags']) # pull out the tags
        print('found the following tags online: ' + str(APItags))
        file.write("Starting with ID: " + row[1] + '\n')
        tagStr = '{\n\t "data" : {\n\t\t"tags" : [' # start the string array
        
        added = 0 # track how many tags were added
        for x in range(2, len(row)):#start at list list[2] and go to list[n] which is tag[n]
            currStr = row[x] # load the tag
            
            #check to make sure we aren't hiring deplorables
            if(currStr == ""):
                print('empty tag at ' + str(x))
                continue
            if(currStr is None):
                print('null tag at ' + str(x))
                continue
            # if the tag already exists for this lead
            if(duplicateTagCheck(response_json['data']['tags'], currStr)):
                print('duplicate tag at ' + str(x))
                continue
            
            tagStr = tagStr + '"' + row[x] + '"'
            if(x is not (len(row) -1)):
                tagStr += ", "
            added +=1
        
        if(added == 0): # no new tags, skip this lead/contact
            file.write("No new tags found, skipping " + str(row[1]) + '\n')
            print("No new tags found, skipping " + str(row[1]) + '\n')
            continue;
        #formatting checks
        APItags = APItags.replace('[',",") # make ...['onlineTag1] into ,'onlineTag1]
        tagStr += APItags + '\n\t}\n}' # make { "data" : {...['localTag0','onlineTag1] }}
        tagStr = tagStr.replace("'", '"') # replace 'tag' with "tag"
        tagStr = tagStr.replace(", ,", ",") # replace "Tag", , "tag2" with "Tag", "tag2"
        tagStr = tagStr.replace(",]", "]") # replace "Tag", , "tag2" with "Tag", "tag2"
        tagStr = tagStr.replace("[,", "[") # replace "Tag", , "tag2" with "Tag", "tag2"
        # tagStr = tagStr + ']\n\t}\n}'
#         tagStr = tagStr.replace("[",'[\n')
#         tagStr = tagStr.replace("]",'\n]')
        file.write("local tags: " + tagStr + '\n')
        
        # not that the tag has been read, downloaded, combined, and built, let's send it
        file.write("sending json: " + tagStr + '\n')
        #response = unirest.post(url, headers = headers, params = tagStr, callback = callBack_function) # send new tags
        print('sending ' + tagStr)
        response = requests.put(url=url, headers=headers,data=tagStr, verify=True)
        if(response.status_code != 200):
            writeAndQuit(response, file)
            continue
        response_json = json.loads(response.text)
        
        file.write("for " + row[0] + " , response code: " + str(response.status_code) + '\n')
        file.write('verified tags: ' + str(response_json['data']['tags']) + '\nDone with #' + str(rowCntr) + '\n')
        
        print("********************for " + row[1] + " , response code: " + str(response.status_code) + "********************")
        print("Done with " + row[0].replace('s', '') + " #" + str(rowCntr) + '\n')
        
print("Goodbye!")
file.close()
        