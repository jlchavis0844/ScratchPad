'''
Created on Nov 4, 2016

@author: jchavis
@param resource(optional) - if no argument exists or argument is not "contacts", defaults to leads

This script will connect to base, and scrape a list of all resources that have "missing@email.com" 
listed as their email address. The script will then null their email field.
'''

# import requests #for API connections  
# import json #for the payloads
# import datetime #log timestamping
# import sys, os, ctypes, tkinter # reading in commandline args
# from tkinter import filedialog
import requests, json, datetime, sys,os,ctypes, tkinter
from tkinter import filedialog

def getToken():
    path = ""
    if(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token")):
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\noe\\token"
    elif(os.path.isfile("\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token")):
        path = "\\\\" + os.environ['COMPUTERNAME'] + "\\NiceOffice\\token"
    else:
        ctypes.windll.user32.MessageBoxW(0, "A token file was not found in your NOE folder, please choose the token file", "Token File", 0)
        FILEOPENOPTIONS = dict(filetypes=[('TOKEN file', '*.*')], title=['Choose token file'])
        root = tkinter.Tk()  # where to open
        root.withdraw()
        #withdraw()  # hide Frame
        path = filedialog.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    if(path == ""):
        ctypes.windll.user32.MessageBoxW(0, "No file was chosen, quiting", "Token File", 0)
        exit("No file picked by user")
    
    file =  open(path, 'r', encoding="utf8")
    token = file.read()
    file.close()
    #print(token)
    return token

time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S') # get timestamp for the log writing.
time = time.replace(" ", "_") # removes spaces from timestamp, not needed

#path = os.path.dirname(__file__) # get current path
path = 'H:\\'
if(path == "" or path == None):
    path = os.getcwd()
print("Starting from " + path)
file = open(path + '\\logs\\emailPurgeLog' + time + '.txt', 'w+') #create and open the log file for this session

resource = "" #create resource variable
if(len(sys.argv) == 1): # check to see if there is a commandline argument
    resource = "leads" #if no commandline arg, default to leads
elif(sys.argv[1] == "contacts"):#if there is a commandline arg, check for contact
    resource = "contacts"
else:#if the commandline arg is anything but contacts, set to leads
    resource = "leads"

# writing log header
file.write("purging missing@email.com from " + resource + " at " + time + "\n")

#load in the API token, for security, the token is saved as plain text locally and is loaded 
token = getToken()

url = "https://api.getbase.com/v2/" + resource # create URL to connect to
qString = {"email" : "missing@email.com", "page": "1", "per_page" : "100"} # build API params
payload = {} # empty body here since first call is a GET
headers = { # headers for the HTTP calls
    'accept':"application/json",
    'authorization': "Bearer " + token,
    'content-type': "application/json"
    }

#send the HTTP call and store result in response
response = requests.request("GET", url, data = payload, headers=headers, params=qString)
data = json.loads(response.text) # load response as a json

if(response.status_code != 200): #if status code is not 200 OK, send warning
    print("Something went wrong, error code " + str(response.status_code))
    file.write("Error code: " + str(response.status_code) + "\n") #write error and quit
    file.write(response.text)
    exit()

if(data["meta"]["count"] == 0):# check for empty results
    print("No results found, quiting") #nothing found, write to log and quit
    file.write(response.text)
    file.close()
    exit()
    
idList = [] # holds id's of the found resources
cont = True
cntr = 1

while(cont == True): # loop to write resource id to a list
    for lead in data["items"]:
        tempID = lead["data"]["id"]
        #file.write(str(tempID) + "\n")
        idList.append(tempID)
        
    if(data["meta"]["count"] == 100): # loop to iterate to the next page if there are more than 100 id's
        cntr += 1
        qString = {"email" : "missing@email.com", "page": str(cntr), "per_page" : "100"} #rebuild params for page n
        response = requests.request("GET", url, data = payload, headers=headers, params=qString) #HTTP call again
        data = json.loads(response.text) # load reponse in data and go back to the top of the loop
    else:#if there are less than 100 results (1 page)
        cont = False #breaks the while loop
        #file.close()

payload = { # creates json to set the email value to null.
    'data' : {
        'email' : None
        }
    }

done = 0 #how many times this loop has ran
for currID in idList:# for every resource with missing@email.com
    url = "https://api.getbase.com/v2/" + resource + "/" + str(currID)# set to proper URI
    file.write(url + "\n") #Write URI to log
    response = requests.request("PUT", url, headers=headers, data = json.dumps(payload), verify = True) #make Call
    file.write("\t result for " + str(currID) + " " + response.text + "\n")#Write response to log
    done += 1 # increase loop count
    print("#" + str(done) + "\tBaseID: " + str(currID) + "\tResponse Code: " + str(response.status_code))#print line to console.
input("Press Enter to continue")
