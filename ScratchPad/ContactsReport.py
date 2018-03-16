'''
Created on Jan 29, 2018

@author: jchavis
'''

import os, tkinter, ctypes, json, requests
import unicodecsv as csv
from io import BytesIO
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime
from datetime import timedelta
from dateutil import tz

def loadOwners():
    global token
    global owners
    if token is None or token == '':
        token = getToken()
    
    oheaders = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token}
    
    oURL = 'https://api.getbase.com/v2/users?per_page=100&status=active'
    oresponse = requests.get(url=oURL, headers=oheaders, verify=True)
    oresponse_json = json.loads(oresponse.text)  # read in the response JSON
    items = oresponse_json['items']
    owners = {}
    
    for item in items:
        owners[item['data']['name']] = item['data']['id']

# this function finds the owner id for the given name and returns owner_id as an int
def getOwner(ownerNum):
    global owners
    if not owners or len(owners) == 0:
        loadOwners()
    
    if(ownerNum == "" or ownerNum == " " or ownerNum is None):
        return ""
    else:
        # return owners[ownerName]
        for k, v in owners.items():
            if(v == ownerNum):
                if(k == ""):
                    return "Not Found"
                else:
                    return k
        return "Not Found"

# This function will check for a text file contacted token which holds the Base API Token in plain text
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


def timeConvert(intime):
    thisTime = intime.replace('T', ' ').replace('Z', '')
    # METHOD 2: Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    # utc = datetime.utcnow()
    utc = datetime.strptime(thisTime, '%Y-%m-%d %H:%M:%S')
    
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)
    
    # Convert time zone
    return utc.astimezone(to_zone)

def writeAndQuit(response, log):
    log.write(response.text)
    print('ERROR: received status code: ' + str(response.status_code) + '\n')
    # log.close()
    # exit(response.status_code)
    
# case insensitive check of all the current api tags with the current tag. If match is found, true, false otherwise
def duplicateTagCheck(APItags, currTag):
    for x in range(len(APItags)):
        if(APItags[x].lower() == currTag.lower()):
            return True
    return False

# need contactback function for Async Unirest contacts
# def contactBack_function(response):
#    print('Empty function, response code was ' + response.code)
    
    
# Setup for the file picker
FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get time stamp for the log writing.
path = os.path.dirname(__file__)  # get current path

# load in the API token, for security, the token is saved as plain text locontacty in the NOE folder
token = getToken()

# get input file
# root = tkinter.Tk()  # where to open
# root.withdraw()  # hide Frame
# csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file
# 
# if(csv_path is None or csv_path == ""):  # if the file picker is closed
#     exit("No file chosen")  # shutdown before log is written

owners = {}


file = open(path + '\\logs\\CallReports' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("starting Call Testing at " + time + '\n')  # write to log
# file.write("using CSV: " + csv_path + '\n')
rowCntr = -1

# start API contact setup, let us try Async contacts with unirest libs
headers = {'Accept': 'application/json',
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + token}

baseURL = 'https://api.getbase.com/v2/contacts'
myParams = {'per_page': '100', 'sort_by' : 'created_at:desc'}
response = requests.get(baseURL, myParams, headers=headers)
dayLimit = (datetime.today() - timedelta(days=7)).replace(tzinfo=tz.tzlocal())

contactArr = []

# with open('H:\\Desktop\\contactOut.csv', encoding="utf8", newline='', errors='ignore') as csvfile:  # open file as UTF-8
#     reader = csv.reader(csvfile, delimiter=',')  # makes the file a csv reader

if(response.status_code == 200):
    contactData = json.loads(response.text)['items']
    for d in contactData:
        # print(timeConvert(d['data']['made_at']))
        thisContact = {}
        
        thisContact['id'] = d['data']['id']
        thisContact['creator_id'] = d['data']['creator_id']
        thisContact['created_at'] = timeConvert(d['data']['created_at'])
        thisContact['creator_name'] = getOwner(d['data']['creator_id'])
        thisContact['updated_at'] = timeConvert(d['data']['updated_at'])
        thisContact['customer_status'] = d['data']['customer_status']
        thisContact['prospect_status'] = d['data']['prospect_status']
        
        if(thisContact['created_at'] >= dayLimit):
            # thisContact = {k: str(v).encode("utf-8") for k,v in thisContact.items()}
            contactArr.append(thisContact)
                      
#     keys = contactArr[0].keys()
#     print(keys)
#     
    while(timeConvert(contactData[len(contactData) - 1]['data']['created_at']) >= dayLimit):
        nextURL = json.loads(response.text)['meta']['links']['next_page']
        response = requests.get(nextURL, headers=headers)
        contactData = json.loads(response.text)['items']
        for d in contactData:
            thisContact = {}
            thisContact['id'] = d['data']['id']
            thisContact['creator_id'] = d['data']['creator_id']
            thisContact['creator_name'] = getOwner(d['data']['creator_id'])
            thisContact['created_at'] = timeConvert(d['data']['created_at'])
            thisContact['updated_at'] = timeConvert(d['data']['updated_at'])
            thisContact['customer_status'] = d['data']['customer_status']
            thisContact['prospect_status'] = d['data']['prospect_status']
              
            if(thisContact['created_at'] >= dayLimit):
                # thisContact = {k: str(v).encode("utf-8") for k,v in thisContact.items()}
                contactArr.append(thisContact) 

        print(contactArr[len(contactArr) - 1]['created_at'])
if(len(contactArr) > 0):  # if merges were detected
    print("contacts found, printing list\n")
    with open('H:\\Desktop\\ContactData.csv', 'wb') as f:  # open csv
        w = csv.DictWriter(f, contactArr[0].keys(), lineterminator='\n')  # make writer
        w.writeheader()  # write header row
        for contact in contactArr:  # write the merges to the merge CSV
            # w.writerow({k:v.decode() for k,v in contact.items()})
            w.writerow(contact)
            # print({k:v.decode() for k,v in contact.items()})
    
        
print("Goodbye!")
file.close()
        
