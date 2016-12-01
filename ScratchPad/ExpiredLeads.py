#!/usr/bin/env python
'''
Created on Nov 16, 2016

@author: jchavis
'''
import datetime  # for comparing time stamps
import os, ctypes, tkinter
import requests, json
import csv
import grequests

PER_PAGE = str(100)
limDays = 30

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
           "TDS Web" : 118595, "Email" : 118948, "TDS MN Print" : 118949, "TDS MN Email" : 118950, "TDS Audit" : 118951,
           "TDS 125 Open Enrollment" : 118952, "None" : 137256, "FHRI My Advisor Magazine" : 150539,
           "Direct Mail Phone-In" : 150540, "Beyond" : 159032, "CareerBuilder" : 159033, "Monster" : 159034,
           "Active Sale" : 184862, "Indeed Ad" : 277038, "Craigs List" : 284440, "Campaign Referral" : 351441,
           "TDS Customer" : 396033
           }


def printResponse(response):
    print(response.status_code)
    print(response.text)
    

def getOwnerName(id):
    for key, value in owners:
        if(value == id):
            return key
    
    return "Not Found"

def getSourceName(id):
    for key, value in sources:
        if(value == id):
            return key
    
    return "Not Found"

# get date from numOfDays ago, positive=past, negative=future
def getLimitDate(numOfDays):
    today = datetime.datetime.now()
    dd = datetime.timedelta(days=numOfDays)
    limit = today - dd
    return limit.strftime('%Y-%m-%d')

def today():
    today = datetime.datetime.now()
    return today.strftime('%Y-%m-%d')

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
        # withdraw()  # hide Frame
        path = tkinter.filedialog.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    if(path == ""):
        ctypes.windll.user32.MessageBoxW(0, "No file was chosen, quiting", "Token File", 0)
        exit()
    
    file = open(path, 'r', encoding="utf8")
    token = file.read()
    file.close()
    # print(token)
    return token

# open log
time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path
file = open(path + '\\logs\\aLeadExpire' + time + '.txt', 'w+')  # create and open the log file for this session
token = "5bbddd26f6610378ef1c848952fd461e5c60bf55d609699ec3b28eb571bb3da7"
#url = "https://api.getbase.com/v2/leads?page=1&per_page="+PER_PAGE+"&owner_id=959081"
url = "https://api.getbase.com/v2/leads?page=1&per_page="+PER_PAGE+"&custom_fields[StatusChange]=" + getLimitDate(limDays)
# qString = {"page": "1", "per_page" : "100"} # build API params
payload = {}  # empty body here since first call is a GET
headers = {  # headers for the HTTP calls
    'accept':"application/json",
    'authorization': "Bearer " + token,
    'content-type': "application/json"
    }

results = []
stop = False
count = 1
while(stop == False):
    # send the HTTP call and store result in response
    response = requests.request("GET", url, data=payload, headers=headers)
    data = json.loads(response.text)  # load response as a json
    returned = data['meta']['count']

    for record in data['items']:
        results.append(record)

    if(returned == PER_PAGE):
        url = data['meta']['links']['next_page']
    else:
        stop = True
        
    print("loop: " + str(count) + '\t' + " returned: " + str(returned))
    print("next page: " + url)
    count += 1
    
print("total results: " + str(len(results)))
file.write("total results: " + str(len(results)) + '\n')
rows = []
header = []

# w = csv.DictWriter(f,lineterminator='\n')  # make writer
for res in results:
    temp = {}
    data = res['data']
    for key in data.keys():
        if(key == 'address'):
            for subkey in data[key]:
                temp[subkey] = data[key][subkey]
        elif(key == 'custom_fields'):
            for subkey in data[key]:
                temp[subkey] = data[key][subkey]
        elif(key == 'tags'):
            for x in range(len(data[key])):
                temp[('tag' + str(x))] = data[key][x]
        else:
            temp[key] = data[key]

                    
    rows.append(temp)  # add to total responses
    for colName in temp:
        if(colName not in header):
            #print("adding header: " + colName)
            header.append(colName)
file.write("Header row: " + '\n')
file.write(str(header) + '\n')
             
f = open(os.getcwd() + '\\expired_' + time + '.csv', 'w', encoding='UTF-8') # open csv
w = csv.DictWriter(f, header, lineterminator='\n')  # make writer
w.writeheader()  # write header row
w.writerows(rows)
f.close()
file.write("finished writing to " + os.getcwd() + '\\expired_' + time + '.csv' + '\n')

AtoB = []
BtoA = []
others = []
async_list = []

for row in rows:
    if(row['New Lead Type'] == "TDS-A Lead" or row['New Lead Type'] == "A Lead"):
        AtoB.append(row)
    elif(row['New Lead Type'] == "B Lead"):
        BtoA.append(row)
    else:
        others.append(row)
if(len(others) > 0):
    file.write("***********************************WARNING************************************" + '\n')
    file.write("The following leads were not either A or B leads" + '\n')
    for row in others:
        info = "id: " + str(row['id']) + ", Name: " + row['first_name'] + " " + row['last_name']
        info += ", lead type: " + row['New Lead Type']
        file.write(info + '\n')
        print("Other: " + info + '\n')
    file.write("*****************************************************************************" + '\n')
    
if(len(AtoB) > 0):   
    for row in AtoB:
        url = "https://api.getbase.com/v2/leads/" + str(row['id'])
        payload = {
                    "data": {
                        "custom_fields": {
                            "New Lead Type": "B Lead",
                            "StatusChange" :  today()},
                            "status": "Unqualified"
                            }
                   }
        # note: unable to install grequests and money patching due to machine limits
        # these should be async calls
        response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)
        printResponse(response)
        file.write("response code: " + response.status_code + '\n')
        
if(len(BtoA) > 0):   
    for row in BtoA:
        url = "https://api.getbase.com/v2/leads/" + str(row['id'])
        payload = {
                    "data": {
                        "custom_fields": {
                            "New Lead Type": "TDS-A Lead",
                            "StatusChange" :  today()},
                            "status": "Available"
                            }
                   }
        response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)
        printResponse(response)
        file.write("response code: " + response.status_code + '\n')
        
file.close()