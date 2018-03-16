'''
Created on Dec 14, 2017
make various and varying changes to the TDS status of a list of leads.
@author: jchavis
'''

import os, tkinter, ctypes, csv, json, requests
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime
from matplotlib.mlab import dist

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
    
# Setup for the file picker
FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get time stamp for the log writing.
path = os.path.dirname(__file__)  # get current path

# load in the API token, for security, the token is saved as plain text locally in the NOE folder
token = getToken()

# get input file
root = tkinter.Tk()  # where to open
root.withdraw()  # hide Frame
csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file

if(csv_path is None or csv_path == ""):  # if the file picker is closed
    exit("No file chosen")  # shutdown before log is written

file = open(path + '.\\logs\\TDSWipe' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("starting tag update at " + time + '\n')  # write to log
file.write("using CSV: " + csv_path + '\n')
rowCntr = -1

# start API call setup, let us try Async calls with unirest libs
headers = {'Accept': 'application/json',
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + token}

baseURL = 'https://api.getbase.com/v2/'

with open(csv_path, encoding="utf8", newline='', errors = 'ignore') as csvfile: # open files as UTF-8
    reader = list(csv.reader(csvfile, delimiter=','))
    
    print('------------------------------------------------ Here we go ------------------------------------------------')
    print('found ' + str(len(reader)) + ' contacts/leads')
    for row in reader:  # iterate through each row (record)
        start_time = datetime.now()
        print("starting row " + str(rowCntr))
        rowCntr += 1  # start at zero
        if(rowCntr == 0):  # skip row 0, we don't need the header names
            continue;  # goes to top of the loop

        #get current lead/contacts info
        url = (baseURL + row[0] + '/' +  row[1]).lower()
        print(url)
        response = requests.get(url=url, headers=headers, data="", verify=True)
        
        #something bad happened, lets give up
        if(response.status_code != 200):
            writeAndQuit(response, file)
            continue
        data = json.loads(response.text) # make a json of the response
#         APItags = str(response_json['data']['tags']) # pull out the tags
#         print('found the following tags online: ' + str(APItags))
        file.write("Starting with ID: " + row[1] + '\n')
        
        custFields = {}
        payload = {}
        payload['data'] = {}
        custFields['TDS'] = 'Yes'

        if "TDS" in data['data']['custom_fields'] and \
        'District' in data['data']['custom_fields'] and \
        data['data']['custom_fields']['District'].startswith("TDS ") and \
        data['data']['custom_fields']['TDS'] == "Yes":
            file.write('This row was skipped ' + str(row) + "\n")
            print('This row was skipped ' + str(row) + "\n")
            continue #District is already tds and tds is No, nothing to change

        if 'District' in data['data']['custom_fields'] and not data['data']['custom_fields']['District'].startswith("TDS "):
            custFields['District'] = "TDS " + data['data']['custom_fields']['District']

#         if 'District' in data['data']['custom_fields']:
#             district = str.replace(data['data']['custom_fields']['District'],"TDS ","")
#             custFields['District'] = district
#             
#         if 'Worksite' in data['data']['custom_fields']:
#             worksite = str.replace(data['data']['custom_fields']['Worksite'],"TDS ","")
#             custFields['Worksite'] = worksite
#             
#         if 'New Lead Type' in data['data']['custom_fields']:
#             leadType = str.replace(data['data']['custom_fields']['New Lead Type'],"TDS-","")
#             custFields['New Lead Type'] = leadType
#             
#         if 'New Section' in data['data']['custom_fields']:
#             section = str.replace(data['data']['custom_fields']['New Section'],"TDS ","")
#             custFields['New Section'] = section
        
        payload['data']["custom_fields"] = custFields
        
        # now that the tag has been read, downloaded, combined, and built, let's send it
        file.write("sending json: " + json.dumps(payload) + '\n')
        #response = unirest.post(url, headers = headers, params = tagStr, callback = callBack_function) # send new tags
        print('sending ' + json.dumps(payload))
        response = requests.put(url=url, headers=headers,data=json.dumps(payload), verify=True)
        if(response.status_code != 200):
            writeAndQuit(response, file)
        response_json = json.loads(response.text)
        
        print("********************for " + row[1] + " , response code: " + str(response.status_code) + "********************")
        print("Done with " + row[0].replace('s', '') + " #" + str(rowCntr))
        timeString = 'Duration: {}'.format(datetime.now() - start_time) + '\n'
        file.write(timeString)
        print(timeString)
        
print("Goodbye!")
file.close()
        