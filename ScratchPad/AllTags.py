'''
Created on Dec 19, 2016

@author: jchavis
'''

import datetime, json, requests, sys, os, csv, ctypes
import tkinter  # for the file picker
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime  # for comparing time stamps



# owners list will hold Key = Name, Value = owner_id
owners = {
    "Robert Lotter"  :768466, "Christa Colton"  :770197, "Steven Chow"  :770199, "Sheila Tedtaotao"  :770211,
    "Data Admin"  :770454, "David Barto"  :774967, "Kristi Breiten"  :775616, "Felipe Diaz"  :775617,
    "Chris Coventry"  :775618, "David Coventry"  :775619, "Rachel Lane"  :775621, "Darren Hulbert"  :775625,
    "Kusuma Suharto"  :775633, "Royce Meredith"  :775638, "Joyce Lavin"  :775768, "Chris McFarland"  :775769,
    "Victor Leonino"  :778823, "Chuck Major"  :783519, "Paul Bruil"  :799111, "Adrian Galvan"  :800987,
    "Duane Kelley"  :813489, "Frank McDermott"  :813490, "Marketing Team"  :825798,
    "newbusiness@ralotter.com"  :828713, "Van Castaneda"  :861053, "Jonathan Pace"  :940653,
    "Gina Gonzales"  :966741, "Dominic Fama"  :973096, "Horacio Rojas"  :977350, "Brian Mendenhall"  :977351,
    "James Chavis"  :991960, "Troy Mathis"  :1000138, "Guillermo Olmedo"  :1000159, "Katherine Seach"  :1000169
    }

sources = {"Direct Mail" : 118573, "Telemarketing" : 118574, "TDS Compliance Clinic" : 118587, "TDS Retired" : 118588,
           "Referral" : 118590, "Guest" : 118592, "FHRI Agent Referral" : 118593, "TDS Referral" : 118594, 
           "TDS Web" : 118595,"Email" : 118948, "TDS MN Print" : 118949, "TDS MN Email" : 118950, "TDS Audit" : 118951, 
           "TDS 125 Open Enrollment" : 118952,"None" : 137256, "FHRI My Advisor Magazine" : 150539, 
           "Direct Mail Phone-In" : 150540, "Beyond" : 159032, "CareerBuilder" : 159033,"Monster" : 159034, 
           "Active Sale" : 184862, "Indeed Ad" : 277038, "Craigs List" : 284440, "Campaign Referral" : 351441,
           "TDS Customer" : 396033
           }

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

# This function returns the difference in seconds of the two given time stamps
# must be of form "%Y-%m-%d %H:%M:%S"
# used to measure against updated_at and created_at
def timeDiff(created, updated):
    created = created.replace("T", " ").replace("Z", "")
    updated = updated.replace("T", " ").replace("Z", "")
    
    t1 = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S")
    difference = t2 - t1
    # print(str(difference.seconds) + " second time difference")
    return difference.seconds  # one hour is 3600 seconds

# serves as a getter for source that reads sources by the key and returns value
# all performs blank, space, and null check (returns empty)
def getSource(sourceName):
    if(sourceName == "" or sourceName == " " or sourceName is None):
        return ""
    else:
        return sources[sourceName]
    
#this function returns the key ( owner name ) given the value (id)
def getOwnerName(ownerID):
    if(ownerID == "" or ownerID == " " or ownerID == 0):
        return "undefined"
    else:
        for key, value in owners.items():
            if(value == ownerID):
                return key
        
        #if this line is reached, we didn't find it
        return "undefined"

# this function finds the owner id for the given name and returns owner_id as an int
def getOwner(ownerName):
    if(ownerName == "" or ownerName == " " or ownerName is None):
        return ""
    else:
        return owners[ownerName]
    
# optional stuff for the file picker
FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path

# load in the API token, for security, the token is saved as plain text locally in the NOE folder
token = getToken()

url = "https://api.getbase.com/v2/tags"
qString = {"page": "1", "per_page" : "100"} # build API params
payload = {} # empty body here since first call is a GET
headers = { # headers for the HTTP calls
    'accept':"application/json",
    'authorization': "Bearer " + token,
    'content-type': "application/json"
    }
response = requests.request("GET", url, data = payload, headers=headers, params=qString)
data = json.loads(response.text) # load response as a json

cont = True
cntr = 1
rows = []
titleRow = ['id','Name', 'created_at', 'updated_at', 'resource_type']
while(cont == True):
    for tag in data["items"]:
        row = {}
        row["id"] = tag["data"]["id"]
        row["name"] =tag["data"]["name"]
        row["created_at"] = tag["data"]["created_at"]
        row["updated_at"] = tag["data"]["updated_at"]
        row["resource_type"] = tag["data"]["resource_type"]
        row["creator"] = getOwnerName(tag["data"]["creator_id"])
        rows.append(row)
        
    if(data["meta"]["count"] == 100):
        qString = {"page": str(cntr), "per_page" : "100"} # build API params
        cntr += 1
        response = requests.request("GET", url, data = payload, headers=headers, params=qString)
        data = json.loads(response.text) # load response as a json
    else:
        cont = False

# make a special CSV of the tags 
if(len(rows) > 0):  # if tags were detected
    with open(os.getcwd() + '\\tags_' + time + '.csv', 'w') as f:  # open csv
        w = csv.DictWriter(f, rows[0].keys(), lineterminator='\n')  # make writer
        w.writeheader()  # write header row
        for row in rows:  # write the merges to the merge CSV
            w.writerow(row)
        
input("press Enter key to continue") # pause at the end of running the program to allow for reading
