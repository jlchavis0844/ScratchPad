'''
Created on Feb 15th, 2018

@author: jchavis
'''
import requests
import json
import time
import os

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


# your oauth token
token = getToken()

# main poll loop - check for new events every 5 seconds
startingPosition = 'top'
while True:

    # loop to recieve all pages of events since we checked last time
    onTop = False
    while not onTop:
        print ('Polling...')
        url = "https://api.getbase.com/v3/leads/stream"
        response = requests.get(url,
                params={'position': startingPosition},
                headers={'Authorization':'Bearer {}'.format(token)})

        if response.status_code != 200:
            raise Exception('Request failed with {}'
                .format(response.status_code))

        # iterate through events and print them
        print(response.json()['items'])
        for item in response.json()['items']:
          print("lead data:\n{}"
                  .format(json.dumps(item['data'], indent=4)));
          if item['meta']['event_type'] == 'updated':
              print("Updated: {}"
                  .format(item['meta']['previous'].keys()))
              print("Old values:\n{}".format(
                  json.dumps(item['meta']['previous'], indent=4)));

        # check if we have reached the top of the stream
        onTop = response.json()['meta']['top']

        # prepare the position for the next request
        startingPosition = response.json()['meta']['position']

    print ("Sleeping...")
    time.sleep(20)
