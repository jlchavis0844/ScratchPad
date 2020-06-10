import datetime  # for comparing time stamps
import os, ctypes, sys
import requests, json
import csv
import argparse
import tkinter.filedialog as fd  # for picking the file
import tkinter
from Tools.scripts.objgraph import readinput
#import grequests # can't use because of dependency failing

owners = {}
sources = {}
resourceType = ""
resourceID = -1

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

token = getToken()

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
    
#start Main Program
        

choice =int(input("Which type of resource will you be duplicating?\n"+\
      "1 : Lead\n2 : Contact\n"))
if(choice != 1 and choice != 2):
    exit()
elif(choice == 1):
    resourceType = "leads"
else:
    resourceType = "contacts"

resourceID = input("Please enter the resource ID below (numbers only)\n")

url = "https://api.getbase.com/v2/" + resourceType + "/"
headers = { # headers for the HTTP calls
    'accept':"application/json",
    'authorization' : "Bearer " + token,
    'content-type': "application/json"
    }

currURL = url + str(resourceID)  # append the id to the API url
response = requests.request("GET", currURL, headers=headers) # make the call# check status code for error, this is most likely a 404 status code because the lead cannot be found
if response.status_code != 200: # 200 is the good code
    print("something went wrong getting data, got status code " + str(response.status_code)) # error message
    readinput("Take a screenshot and send this to James then hit enter to quit")
    exit()

data = json.loads(response.text) # make a json
print("You'll be duplicating " + data['data']['first_name'] + " " + data['data']['last_name'] + "\n")
if(input('press 9 to quit or any other number to continue\n')) == 9:
   exit()

loadOwners()
ownerList = list(owners.keys())

cntr = 0
for id in ownerList:
    print(str(cntr) + ": " + str(id))
    cntr = cntr + 1

newOwner = int(input("Who is the new owning agent?\n"))
ownerName = ownerList[newOwner]
print("New owner " + ownerName + " : " +  str(owners[ownerName]))


del data['meta']
del data['data']['id']

if 'unqualified_reason_id' in data['data']:
    del data['data']['unqualified_reason_id']
    
del data['data']['created_at'] # create and update dates are not needed
del data['data']['updated_at']
del data['data']['creator_id']

choice = input("Would you like to insert a tag?\nNote: Tags are Case Sensitive\n"+\
                   "1 : Yes\n2 : No\nAnything else to quit\n")

if(int(choice) == 1):
    newTag = input("Enter Tag\n")
    data['data']['tags'].append(str(newTag))
    print("tags: \n" + str(data['data']['tags']))

data['owner_id'] = owners[ownerName]
print(json.dumps(data))
response = requests.post(url="https://api.getbase.com/v2/" + resourceType, headers = headers, data=json.dumps(data), verify=True)

if response.status_code != 200:
                print("something went wrong creating a lead, got status code " + str(response.status_code) + '\n')
                file.write("something went wrong creating a lead, got status code " + str(response.status_code)+ '\n')
                print(json.dumps(data))
                exit()

print("Done!\n")
data = json.loads(response.text)
print("New ID: " + str(data['data']['id']))
input("Press any key to continue")


        
