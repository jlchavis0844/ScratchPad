'''
Created on Jul 6th, 2021
@author: jchavis
'''

import datetime, json, requests, sys, os, csv, ctypes, io
import tkinter  # for the file picker
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime  # for comparing time stamps

token = '628d2355-2fff-4b28-bafb-f850d21dd3fe'
owners = {}
sources = {}
dupes = {}
cleaned = []
deletes = {}
merged = []
breakError = False
mergeCount = 0;
CustomFields = {}
CustomFields['TDS'] = '17bUuUQWziIWa1hkeTWt'
CustomFields['Business Phone Ext'] = '3590V2fA63u07TSLyCbZ'
CustomFields['Worksite Email'] = '4JDTfVfscndtYwVN2UZ2'
CustomFields['Mktg ID'] = '8dV7h0BRR7brSXlHrNGq'
CustomFields['Client ID'] = 'GLbD547pBUu8TUrSbgHm'
CustomFields['Section'] = 'GRB7GaJBunRMnTiso0kb'
CustomFields['Worksite'] = 'HWcJOmTpd4nIZfjBRtu2'
CustomFields['Cell Phone'] = 'IoyPasBDiLWSVG405xel'
CustomFields['What can we help you with?'] = 'KFwTPPpj4uEZcYofrws8'
CustomFields['Response Note'] = 'MXo5st2sTItGumUsnwk6'
CustomFields['Organization'] = 'NsxyiF8wdfYRCZa5p4K1'
CustomFields['Best time to reach you'] = 'OW6XD8zdddenLtrjfaRL'
CustomFields['Worksite Phone'] = 'PRKCT9Cn9xe2HIDLRnWg'
CustomFields['Business Phone'] = 'Sr3UsJccOD00ruBqDdPh'
CustomFields['Alt Email 2'] = 'UnAnsCvEX1IDgF8Dy7ix'
CustomFields['Alt Phone Number'] = 'WR6obA0cP5inixUXacD9'
CustomFields['Zen Owner'] = 'aUoQXceZKTMhRFj2tJna'
CustomFields['Alt Phone'] = 'kpvVTOOoMGBZH8N41KEG'
CustomFields['Home Phone'] = 'lCtZ0Pvlh8pliFclc3DE'
CustomFields['Lead Type'] = 'm9DJJl1aoaTM64Netuwd'
CustomFields['Alt Email'] = 'n5YNh0RyKBuEnM6HiR42'
CustomFields['District'] = 'rAkpg39t7kNoegmI3qAZ'
CustomFields['Contact Status'] = 's2DiyDIOz6T9XBrAmdZT'
CustomFields['District Phone'] = 'udPNVvQSdZSsUDQQOmDo'
CustomFields['HL Phone'] = 'vm6JD3PNWkE6ULEQZuMB'



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

def loadOwners():
    global token
    global owners
#     if token is None or token == '':
#         token = getToken()
    
    oheaders = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token}
    
    oURL = 'https://rest.gohighlevel.com/v1/users'
    oresponse = requests.get(url=oURL, headers=oheaders, verify = True)
    oresponse_json = json.loads(oresponse.text)  # read in the response JSON
    items = oresponse_json['items']
    owners = {}
    
    for item in items:
        owners[item['users']['name']] = item['users']['id']

# this function finds the owner id for the given name and returns owner_id as an int
def getOwner(ownerName):
    global owners
    if not owners or len(owners) == 0:
        loadOwners()
    
    if(ownerName == "" or ownerName == " " or ownerName is None):
        return ""
    else:
        return owners[ownerName]
    
def loadDupes():
    tDupes= {}  # holds the data object for the json
    global file
    with open(csv_path, encoding="utf-8", newline='', errors='ignore') as csvfile:  # open file as UTF-8
        reader = csv.reader(csvfile, delimiter=',')  # makes the file a csv reader
        rowCntr = -1  # start index, will track which row the process is on

        for row in reader:  # iterate through each row (record)
            rowCntr += 1  # start at zero
            if(rowCntr == 0):  # skip row 0, we don't need the header names
                continue;  # goes to top of the loop
            
            
            if len(tDupes) >0:
                dupes.clear()
            
            #Lets load the CSV values into JSON objects data, address, or custom
            info = {
                'count' : row[0],
                'Contact Id' : row[1],
                'Name' : row[2],
                'First Name' : row[3],
                'Last Name' : row[4],
                'Business Name' : row[5],
                'DND' : row[6],
                'Phone' : row[7],
                'Email' : row[8],
                'Created' : row[9],
                'Source' : row[10],
                'Type' : row[11],
                'Updated' : row[12],
                'Last Activity' : row[13],
                'Last Appointment' : row[14],
                'Assigned' : row[15],
                'Tags' : row[17],
                'Address (full)' : row[18],
                'Address (1st Line)' : row[19],
                'City' : row[20],
                'Postal Code' : row[21],
                'State' : row[22],
                'Birth Date' : row[23],
                'Worksite Email' : row[28],
                'Worksite' : row[32],
                'Cell Phone' : row[33],
                'Response Note' : row[35],
                'Worksite Phone' : row[38],
                'Business Phone' : row[39],
                'Zen Owner' : row[42],
                'Alt Phone' : row[44],
                'Home Phone' : row[45],
                'Lead Type' : row[46],
                'District' : row[47],
                'District Phone' : row[49],
                'HL Phone' : row[50]
                }
            
            key = info['Contact Id']
            tDupes[key] = info
            print("added " + key + "\t" + str(tDupes[key]))
            file.write(json.dumps(info))

            
    print(len(tDupes))
    return tDupes

def mergeTags(m,s):
    masterList = m.split(',')
    slaveList = s.split(',')
    
    for tag in slaveList:
        if tag not in masterList:
            masterList.append(tag)
    
    return ','.join(masterList)
        

def findDupes(lead):
    global dupes
    foundDupes=[]
    #dupeKeys.append(lead['Contact Id'])
    tFname = lead['First Name']
    tLname = lead['Last Name']
    tPhone = lead['Phone']
    
    for cid in dupes:
        if dupes[cid]['Phone'] == tPhone and dupes[cid]['Last Name'] == tLname and dupes[cid]['First Name'] == tFname:
              foundDupes.append(dupes[cid])
              
    return foundDupes

def mergeDupes(mergeList):
    global dupes, deletes, cleaned, CustomFields
    delList = mergeList
    #mergeList.sort(key='Updated')
    mergeList = sorted(mergeList,key = lambda i: i['Updated'], reverse=True)
    toDelete = []
    master = mergeList[0]
    
    while len(mergeList) > 1:
        slave = mergeList[1]
        
        if len(master['Tags']) == 0:
            master['Tags'] = slave['Tags']
        elif master['Tags'] != slave['Tags']:
            master['Tags'] = mergeTags(master['Tags'], slave['Tags'])
        
        if master['Business Name'] is None or len(master['Business Name']) == 0:
            master['Business Name'] = slave['Business Name']
            
        if master['Email'] is None or len(master['Email']) == 0:
            master['Email'] = slave['Email']
        elif slave['Email'] is not None and slave['Email'] != master['Email']:
            master['Alt Email'] = slave['Email']
            
        if master['Address (full)'] is None or len(master['Address (full)']) == 0:
            master['Address (full)'] = slave['Address (full)']
        
        if master['Address (1st Line)'] is None or len(master['Address (1st Line)']) == 0:
            master['Address (1st Line)'] = slave['Address (1st Line)']        
        
        if master['City'] is None or len(master['City']) == 0:
            master['City'] = slave['City']        
        
        if master['Postal Code'] is None or len(master['Postal Code']) == 0:
            master['Postal Code'] = slave['Postal Code']        
        
        if master['State'] is None or len(master['State']) == 0:
            master['State'] = slave['State']        
        
        if master['Birth Date'] is None or len(master['Birth Date']) == 0:
            master['Birth Date'] = slave['Birth Date']        
        
#         if master['Business Phone Ext'] is None or len(master['Business Phone Ext']) == 0:
#             master['Business Phone Ext'] = slave['Business Phone Ext']        
        
        if master['Worksite Email'] is None or len(master['Worksite Email']) == 0:
            master['Worksite Email'] = slave['Worksite Email']        
                       
        if master['Worksite'] is None or len(master['Worksite']) == 0:
            master['Worksite'] = slave['Worksite']
                       
        if master['Cell Phone'] is None or len(master['Cell Phone']) == 0:
            master['Cell Phone'] = slave['Cell Phone']
                       
        if master['Response Note'] is None or len(master['Response Note']) == 0:
            master['Response Note'] = slave['Response Note']
                       
        if master['Worksite Phone'] is None or len(master['Worksite Phone']) == 0:
            master['Worksite Phone'] = slave['Worksite Phone']
                       
        if master['Business Phone'] is None or len(master['Business Phone']) == 0:
            master['Business Phone'] = slave['Business Phone']
                       
        if master['Zen Owner'] is None or len(master['Zen Owner']) == 0:
            master['Zen Owner'] = slave['Zen Owner']
                       
        if master['Home Phone'] is None or len(master['Home Phone']) == 0:
            master['Home Phone'] = slave['Home Phone']
                       
        if master['District'] is None or len(master['District']) == 0:
            master['District'] = slave['District']
                                 
        if master['District Phone'] is None or len(master['District Phone']) == 0:
            master['District Phone'] = slave['District Phone']
                       
                       
        if master['HL Phone'] is None or len(master['HL Phone']) == 0:
            master['HL Phone'] = slave['HL Phone']
                       
                       
        if (master['Alt Phone'] is None or len(master['Alt Phone'])) == 0 and (slave['Phone'] is not None and len(slave['Phone']) != 0):
            master['Alt Phone'] = slave['Alt Phone']
            
        toDelete.append(slave['Contact Id'])
        del dupes[slave['Contact Id']]
        del mergeList[1]
    
    cleaned.append(mergeList[0])
    deletes[master['Contact Id']] = toDelete
    del dupes[master['Contact Id']]
    
def UpdateContacts():
    global cleaned, file, breakError
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
        
    
    for contact in cleaned:
        url = 'https://rest.gohighlevel.com/v1/contacts/' + contact['Contact Id']

        #lets just rebuild to handle the custom fields. Shutup
        data = {}
        tags = []
        cFields = {}
        data['firstName'] = contact['First Name']
        data['lastName'] = contact['Last Name']
        data['name'] = contact['First Name'] + ' ' + contact['Last Name']
        data['email'] = contact['Email']
        data['phone'] = contact['Phone']
        data['source'] = contact['Source']
        
        if len(contact['Address (1st Line)']) != 0:
            data['address1'] = contact['Address (1st Line)']
        elif len(contact['Address (full)']) != 0:
            data['address1'] = contact['Address (full)']

        data['city'] = contact['City']
        data['state'] = contact['State']
        data['postalCode'] = contact['Postal Code']
        data['companyName'] = contact['First Name']
        data['tags'] = contact['Tags'] #conver to string?

        cFields[CustomFields['Worksite']] = contact['Worksite']
        cFields[CustomFields['Worksite Email']] = contact['Worksite Email']
        cFields[CustomFields['Cell Phone']] = contact['Cell Phone']
        cFields[CustomFields['Response Note']] = contact['Response Note']
        cFields[CustomFields['Worksite Phone']] = contact['Worksite Phone']
        cFields[CustomFields['Business Phone']] = contact['Business Phone']
        cFields[CustomFields['Zen Owner']] = contact['Zen Owner']
        cFields[CustomFields['Alt Phone']] = contact['Alt Phone']
        cFields[CustomFields['Home Phone']] = contact['Home Phone']
        cFields[CustomFields['District']] = contact['District']
        cFields[CustomFields['District Phone']] = contact['District Phone']
        cFields[CustomFields['HL Phone']] = contact['HL Phone']
        
        
        
        data['customField'] = cFields
        
        payload = json.dumps(data)
        print(payload)
        response = requests.request("PUT", url, headers=headers, data=payload)
        response_json = json.loads(response.text)  # read in the response JSON
        file.write("Finished with status code: " + str(response.status_code) + "\n")
        print("Finished with status code: " + str(response.status_code) + "\n")
        
        if response.status_code != 200:
            file.write("ERROR*************************************************************\n\n")
            file.write("Could not complete the update, returned: " + str(response.status_code) + '\n')
            file.write("CHECK THE LOG FOR:\n")
            file.write(json.dumps(payload, indent=4))
            file.write("\n\n")
            print("ERROR*************************************************************\n\n")
            print("Could not complete the upsert, returned: " + str(response.status_code) + '\n')
            print("CHECK THE LOG FOR: " + data["firstName"] + " " + data["lastName"])
            breakError = True
            return None
        else:
            #created = response_json['contact']['dateAdded']  # store the time stamp for when the lead was created
            #updated = response_json['contact']['fingerPrint']  # store the time stamp for when the lead was updated
            #file.write("created: " + created + '\n')  # write the created time stamp to log
            file.write("updated: " + json.dumps(response_json) + '\n')  # write the updated time stamp to the log
            CID = contact['Contact Id']
            
            for thisDel in deletes[CID]:
                DeleteContact(thisDel)
            
def DeleteContact(cid):
    global deletes, breakError, file
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
        
    payload = {}
    #for contact in deletes:
    url = 'https://rest.gohighlevel.com/v1/contacts/' + cid
    response = requests.request("DELETE", url, headers=headers, data=payload)
        #response_json = json.loads(response.text)  # read in the response JSON
    file.write("Finished with status code: " + str(response.status_code) + "\n")
    print(cid + " Finished with status code: " + str(response.status_code) + "\n")
        
    if response.status_code != 200:
        file.write("ERROR*************************************************************\n\n")
        file.write("Could not complete the delete, returned: " + str(response.status_code) + '\n')
        file.write("CHECK THE LOG FOR:\n")
        #file.write(json.dumps(response, indent=4))
        file.write("\n\n")
        print("ERROR*************************************************************\n\n")
        print("Could not complete the delete, returned: " + str(response.status_code) + '\n')
        print("CHECK THE LOG FOR: " + cid)
        #breakError = True
        #return None
    else:
#             created = response_json['contact']['created_at']  # store the time stamp for when the lead was created
#             updated = response_json['data']['updated_at']  # store the time stamp for when the lead was updated
#             file.write("created: " + created + '\n')  # write the created time stamp to log
        file.write("Deletes: " + cid + '\t' + str(response.status_code) + '\n')  # write the updated time stamp to the log
        
    
# optional stuff for the file picker
FILEOPENOPTIONS = dict(defaultextension='.csv', filetypes=[('CSV file', '*.csv'), ('All files', '*.*')])
time = datetime.now().strftime('%Y-%m-%d_%H%M%S')  # get timestamp for the log writing.
path = os.path.dirname(__file__)  # get current path


# get input file
root = tkinter.Tk()  # where to open
root.withdraw()  # hide Frame
csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file

if(csv_path is None or csv_path == ""):  # if the file picker is closed
    exit("No file chosen")  # shutdown before log is written

file = open(path + '.\\logs\\importLog' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("starting leads import at " + time + '\n')  # write to log
file.write("using CSV: " + csv_path + '\n')


print('**********************************************************************************')
file.write('**********************************************************************************')
file.write('Loading dupes')
dupes = loadDupes()
dupeCnt = len(dupes)
file.write('Loaded ' + str(len(dupes)) + " rows")
print('Loaded ' + str(len(dupes)) + " rows")

while len(dupes) != 0:
    values_view = dupes.values()
    value_iterator = iter(values_view)
    first_value = next(value_iterator)
    
    dupeList = findDupes(first_value)
    mergeDupes(dupeList)
        
print('Keeping ' + str(len(cleaned)) +'\nDeleting ' + str(len(deletes)))
if len(cleaned) + len(deletes) != dupeCnt:
    print('WARNING: COUNTS DO NOT MATCH!' )

UpdateContacts()
# if(breakError == False):
#     DeleteContacts()


print('Kept ' + str(len(cleaned)) +'\nDeleted ' + str(len(deletes)))
    
file.close()
input("press Enter key to continue") # pause at the end of running the program to allow for reading
