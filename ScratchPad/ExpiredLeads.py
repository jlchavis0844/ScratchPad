#!/usr/bin/env python
'''
Created on Nov 16, 2016
Add comments and verified some small logic changes - 12/22/2016
added partial unirest call for multithreading - 12/22/2016
@author: jchavis
'''
import datetime  # for comparing time stamps
import os, ctypes, tkinter
import requests, json
import csv
import unirest
#import grequests # can't use because of dependency failing

PER_PAGE = str(100) # how many results should be returned at one time
limDays = 30 # The amount of days the leads should flip after

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

#this is meant to be the call back function for an sync unirest call
def callback_function(response):
    print(response.raw_body())



#This method is for debugging purposes
def printResponse(response):
    print(response.status_code)
    print(response.text)
    
#given the id(value), return the name (key)
def getOwnerName(val):
    for key, value in owners:
        if(value == val):
            return key
    
    return "Not Found"

# given the id, get the source name
def getSourceName(val):
    for key, value in sources:
        if(value == val):
            return key
    
    return "Not Found"

# get date from numOfDays ago, positive=past, negative=future
def getLimitDate(numOfDays):
    today = datetime.datetime.now() # Today
    dd = datetime.timedelta(days=numOfDays) # for the arithmetic process
    limit = today - dd # the result of the subtraction
    return limit.strftime('%Y-%m-%d') # format the return

# returns todays date in the standard Yyyy-mm-dd format
def today():
    today = datetime.datetime.now()
    return today.strftime('%Y-%m-%d')

# this method will attempt to find a file containing the API token
def getToken():
    path = ""
    if(os.path.isfile("C:\\Apps\\NiceOffice\\token")): # search the C:\Apps folder
        path = "C:\\Apps\\NiceOffice\\token"
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

# open log
time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path
file = open(path + '\\logs\\aLeadExpire' + time + '.txt', 'w+')  # create and open the log file for this session
token = getToken()
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
count = 1 # will track the page count, start on page 1
while(stop == False):
    # send the HTTP call and store result in response
    response = requests.request("GET", url, data=payload, headers=headers)
    data = json.loads(response.text)  # load response as a json
    returned = data['meta']['count'] # how many results

    for record in data['items']: # write results to list
        results.append(record)

    if(returned == PER_PAGE): # if the returned is equal to the max, there is another page
        url = data['meta']['links']['next_page'] # load the next page which is given as part of the return message from Base
    else:
        stop = True
        
    print("loop: " + str(count) + '\t' + " returned: " + str(returned))
    print("next page: " + url)
    count += 1 # increase count, not needed
    
print("total results: " + str(len(results)))
file.write("total results: " + str(len(results)) + '\n') # write to the log file the number of results
rows = [] # holds a record
header = [] # holds column names (keys)

#go through all results
for res in results:
    temp = {}
    data = res['data']
    for key in data.keys(): # go through record fields
        if(key == 'address'): # find address and treat as a seperate list
            for subkey in data[key]:
                temp[subkey] = data[key][subkey]
        elif(key == 'custom_fields'): # if this is a custom field, load in seperate list
            for subkey in data[key]:
                temp[subkey] = data[key][subkey]
        elif(key == 'tags'):# tags are loaded into an array
            for x in range(len(data[key])):
                temp[('tag' + str(x))] = data[key][x]
        else: # if it isn't a special or custom field, add it to main list
            temp[key] = data[key]

    # here the record is now complete, add the row
    rows.append(temp)  # add to total responses
    
    for colName in temp:# check to see if the column name has been added yet 
        if(colName not in header):
            #print("adding header: " + colName)
            header.append(colName) # if the column name hasn't been added to the list yet, append it
            
file.write("Header row: " + '\n') # write to the log the header row
file.write(str(header) + '\n') # the actual row

#now we will write the results to the CSV file.
f = open(os.getcwd() + '\\expired_' + time + '.csv', 'w', encoding='UTF-8') # open csv
w = csv.DictWriter(f, header, lineterminator='\n')  # make writer
w.writeheader()  # write header row
w.writerows(rows) # write ALL the records as CSV rows
f.close()  # cl;ose the file after writing
file.write("finished writing to " + os.getcwd() + '\\expired_' + time + '.csv' + '\n')

AtoB = [] # holds leads that are moving from a to b
BtoA = [] # holds the leads that moving from b to a
others = [] # problem children
async_list = [] # not used

# for each result
for row in rows: # we will now toggle from a to b or b to a
    if(row['New Lead Type'] == "TDS-A Lead" or row['New Lead Type'] == "A Lead"):
        AtoB.append(row)
    elif(row['New Lead Type'] == "B Lead"):
        BtoA.append(row)
    else: # if this lead is neither a TDS-A nor B lead, dump it here
        others.append(row)
        
if(len(others) > 0): # well, poop. Some leads were not TDS-A or B leads. What are we going to do with them?
    file.write("***********************************WARNING************************************" + '\n') # write them to the log!
    file.write("The following leads were not either A or B leads" + '\n')
    for row in others:
        info = "id: " + str(row['id']) + ", Name: " + row['first_name'] + " " + row['last_name']
        info += ", lead type: " + row['New Lead Type']
        file.write(info + '\n')
        print("Other: " + info + '\n')
    file.write("*****************************************************************************" + '\n')
    
if(len(AtoB) > 0): # let's do the old switchero
    for row in AtoB:
        url = "https://api.getbase.com/v2/leads/" + str(row['id'])
        payload = { # here we load the body of the put request
                    "data": {
                        "custom_fields": {
                            "New Lead Type": "B Lead", # change to a B lead
                            "StatusChange" :  today()},
                            "status": "Unqualified" # mark as unqualified
                            }
                   }
        # note: unable to install grequests and money patching due to machine limits
        # these should be async calls
        #TODO: Make this section async. Use futures and call backs. Fix it up something real nice like............
        response = requests.request("PUT", url, data=json.dumps(payload), headers=headers) # make the API call
        printResponse(response) # show the response
        file.write("response code: " + response.status_code + '\n')
        
if(len(BtoA) > 0): # switching from B leads to A leads
    for row in BtoA:
        url = "https://api.getbase.com/v2/leads/" + str(row['id'])
        payload = { # to body to essentially undo what we did above
                    "data": {
                        "custom_fields": {
                            "New Lead Type": "TDS-A Lead",
                            "StatusChange" :  today()},
                            "status": "Available"
                            }
                   }
        #TODO: Make these async calls using grequests or unirest
        #response = unirest.put(url, params = json.dumps(payload), headers = headers, callback = callback_function)
        response = requests.request("PUT", url, data=json.dumps(payload), headers=headers) # make the API calls
        #printResponse(response)
        file.write("response code: " + response.status_code + '\n')
        
file.close() #eexit the program