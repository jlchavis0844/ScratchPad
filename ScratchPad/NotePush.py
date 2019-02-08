'''
Created on Mar 15, 2017

@author: jchavis

Quick program to push a new note to the contact. To expanded later
The CSV file should be outlined as such...

NOTE: the content portion of the CSV should contain char(10) {char(13) optional} and not \n
Python will auto escape \n to \\n. Why not let it convert char(10) to \n for you?

ContactID    Type    Content
1223456      lead    This is the note content

as of 3/15/2017 - no error checking, options, or args.
'''


import datetime, json, requests, sys, os, csv, ctypes
import tkinter  # for the file picker
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime  # for comparing time stamps


#This function will check for a text file called token which holds the Base API Token in plain text
# this token will be loaded, read, and stored as the token variable that is returned
# the function will read this computer's name and then check the network shared drive locations
#     \\NAME\noe\token
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

file = open(path + '\\logs\\notesLog' + time + '.txt', 'w+')  # create and open the log file for this session
file.write("starting note import at " + time + '\n')  # write to log
file.write("using CSV: " + csv_path + '\n')

with open(csv_path, encoding="utf8", newline='', errors='ignore') as csvfile:  # open file as UTF-8
    reader = csv.reader(csvfile, delimiter=',')  # makes the file a csv reader
    
    print('**************************************************************************************')
    rowCntr = -1  # start index, will track which row the process is on

    for row in reader:  # iterate through each row (record)
        rowCntr += 1  # start at zero
        if(rowCntr == 0):  # skip row 0, we don't need the header names
            continue;  # goes to top of the loop

        # perform a few null checks first, basic error checking. Don't judge me, I've got things to do.
        # Yes, it None, not null. No, I don't care.
        if row is None or row[0] is None or row[1] is None or row[2] is None:
            file.write("something is wrong with the row #" + str(rowCntr) + "\nRow = " + str(row) + "\n")
            print("something is wrong with the row #" + str(rowCntr) + "\nRow = " + str(row) + "\n")
            continue
        
        # now that we have passed the rigorous error checking, build the note create call
        payload = {
            'data': {
                'resource_type': str(row[1]).lower(), # lead or contact
                'resource_id': int(row[0]), # Base ID
                'content': str(row[2]) # the string of the note
            }, # the rest is static. Yes, you need the meta dict
            'meta': {
                'type': 'note'
            }
        }

        #build header for API call
        headers = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + token
                 }
        
        url='https://api.getbase.com/v2/notes'  # decide how the leads will merge on upsert if needed
        response = requests.post(url=url, headers=headers, data=json.dumps(payload), verify=True)  # send it
        response_json = json.loads(response.text)  # read in the response JSON
        
        file.write ("attempt to push to contact " + row[0] + "\n " + response.text + "\n")
        print("attempt to push to contact " + row[0] + "\n" + response.text + "\n")
        
input("press Enter key to continue") # pause at the end of running the program to allow for reading
        