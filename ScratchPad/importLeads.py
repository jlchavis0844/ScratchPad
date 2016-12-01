'''
Created on Nov 11, 2016

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

merged = []
mergeCount = 0;

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

# get input file
root = tkinter.Tk()  # where to open
root.withdraw()  # hide Frame
csv_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file

if(csv_path is None or csv_path == ""):  # if the file picker is closed
    exit("No file chosen")  # shutdown before log is written

file = open(path + '\\logs\\importLog' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("starting leads import at " + time + '\n')  # write to log
file.write("using CSV: " + csv_path + '\n')

with open(csv_path, encoding="utf8", newline='', errors='ignore') as csvfile:  # open file as UTF-8
    reader = csv.reader(csvfile, delimiter=',')  # makes the file a csv reader
    
    print('**************************************************************************************')
    rowCntr = -1  # start index, will track which row the process is on

    for row in reader:  # iterate through each row (record)
        rowCntr += 1  # start at zero
        if(rowCntr == 0):  # skip row 0, we don't need the header names
            continue;  # goes to top of the loop
        
        payload = {}  # will hold the reqests payload
        data = {}  # holds the data object for the json
        custom_fields = {}  # custom fields JSON obect
        address = {}  # the address json object
        data["email"] = row[0]  # each column is mapped to a json object 
        data["source_id"] = getSource(row[1])
        custom_fields["Our Region"] = row[2]
        custom_fields["TDS"] = row[3]
        custom_fields["Territory"] = row[4]
        data["owner_id"] = getOwner(row[5])
        data["first_name"] = row[6]
        data["last_name"] = row[7]
        address["line1"] = row[8]
        address["city"] = row[9]
        address["postal_code"] = row[11]
        custom_fields["Home Phone"] = row[12]
        data["mobile"] = row[13]
        custom_fields["NDNC"] = row[14]
        custom_fields["NDNC HmPhone"] = row[15]
        custom_fields["NDNC ExpDate"] = row[16]
        custom_fields["Worksite"] = row[17]
        custom_fields["Worksite Phone"] = row[18]
        custom_fields["Worksite Email"] = row[19]
        custom_fields["District"] = row[20]
        custom_fields["District Phone"] = row[21]
        custom_fields["Alt Phone"] = row[22]
        custom_fields["Business Phone"] = row[23]
        custom_fields["Business Phone Ext"] = row[24]
        custom_fields["DOB"] = row[25]
        custom_fields["Gender"] = row[26]
        custom_fields["Annual Salary"] = row[27]
        custom_fields["YrsPERS"] = row[28]
        custom_fields["YrsSTRS"] = row[29]
        custom_fields["Planned Retire"] = row[30]
        custom_fields["Beneficiary"] = row[31]
        custom_fields["Beneficiary DOB"] = row[32]
        custom_fields["Spouse Name"] = row[33]
        custom_fields["Mktg ID"] = row[34]
        custom_fields["New Lead Type"] = row[35]
        custom_fields["New Section"] = row[36]
        custom_fields["Client ID"] = row[37]
        custom_fields["Agent ID"] = row[38]
        custom_fields["Response Note"] = row[39]

        temp = {}  # holds values that are not ""
        for x in data:  # go through data object
            if(data[x] != ""):  # only copy the non-"" values
                temp[x] = data[x]
        
        data = temp
        
        temp = {}  # repeat above process
        for x in custom_fields:
            if(custom_fields[x] != ""):
                temp[x] = custom_fields[x]
        
        custom_fields = temp
        
        temp = {}  # repeat above process
        for x in address:
            if(address[x] != ""):
                temp[x] = address[x]
        address = temp
        
        # add the address and custom fields object to the data json object
        if(len(custom_fields) != 0):
            data["custom_fields"] = custom_fields
            
        if(len(address) != 0): # check and add address if not empty( No address:{})
            data["address"] = address
            
        payload["data"] = data
        file.write(json.dumps(payload) + '\n')
        print(json.dumps(payload, indent=4))

        headers = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token}

        url = ""  # decide how the leads will merge on upsert if needed
        if "Worksite" in custom_fields and "District" in custom_fields:  # if worksite is not empty
            url = "https://api.getbase.com/v2/leads/upsert?first_name=" + data["first_name"] + "&last_name="\
            + data["last_name"] + "&custom_fields[District]=" + custom_fields["District"] + "&custom_fields[Worksite]="\
            + custom_fields["Worksite"]
        elif "Worksite" in custom_fields:# if there is no district but there is a worksite 
            url = "https://api.getbase.com/v2/leads/upsert?first_name=" + data["first_name"] + "&last_name="\
            + data["last_name"] + "&custom_fields[Worksite]=" + custom_fields["Worksite"]
        elif "District" in custom_fields.keys():  # if worksite is empty, but not distric
            url = "https://api.getbase.com/v2/leads/upsert?first_name=" + data["first_name"] + "&last_name="\
            + data["last_name"] + "&custom_fields[District]=" + custom_fields["District"]
        else:  # if worksite and district is empty, just first and last name
            url = "https://api.getbase.com/v2/leads/upsert?first_name=" + data["first_name"] + "&last_name="\
            + data["last_name"]
            
        file.write("URI: " + url + '\n')  # write the URI to the log file
        response = requests.post(url=url, headers=headers, data=json.dumps(payload), verify=True)  # send it
        response_json = json.loads(response.text)  # read in the response JSON
        created = response_json['data']['created_at']  # store the time stamp for when the lead was created
        updated = response_json['data']['updated_at']  # store the time stamp for when the lead was updated
        file.write("created: " + created + '\n')  # write the created time stamp to log
        file.write("updated: " + updated + '\n')  # write the updated time stamp to the log
        
        if(timeDiff(created, updated) > 60):  # if the created and updated are more than a minute apart
            print("****WARNING, THIS LEAD WAS MERGED*****" + '\n')
            file.write("****WARNING, THIS LEAD WAS MERGED*****" + '\n')
            mergeCount += 1
            thisMerge = {}  # build array of merged leads
            thisMerge['BaseID'] = response_json['data']['id']
            thisMerge['Client ID '] = response_json['data']['custom_fields']['Client ID']
            thisMerge['First'] = response_json['data']['first_name']
            thisMerge['Last'] = response_json['data']['last_name']
            print(list(thisMerge.keys()))
            print(list(thisMerge.values()))
                   
            merged.append(thisMerge)  # add to merged list
            
# write merged to the log file
file.write("the following leads were merged\n")        
for item in merged:
    file.write(str(item) + '\n')

# make a special CSV of the merges 
if(mergeCount > 0):  # if merges were detected
    with open(os.getcwd() + '\\mergeReport_' + time + '.csv', 'w') as f:  # open csv
        w = csv.DictWriter(f, merged[0].keys(), lineterminator='\n')  # make writer
        w.writeheader()  # write header row
        for merge in merged:  # write the merges to the merge CSV
            w.writerow(merge)
        
input("press any key to continue") # pause at the end of running the program to allow for reading
