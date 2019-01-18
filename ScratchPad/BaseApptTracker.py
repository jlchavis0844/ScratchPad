import requests
import json
import time
import os

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

# your oauth token
token = getToken()

# main poll loop - check for new events every 5 seconds
startingPosition = 'top'
while True:

    # loop to recieve all pages of events since we checked last time
    onTop = False
    while not onTop:
        print ('Polling...')
        url = "https://api.getbase.com/v3/appointments/stream"
        response = requests.get(url,
                params={'position': startingPosition},
                headers={'Authorization':'Bearer {}'.format(token)})

        if response.status_code != 200:
            raise Exception('Request failed with {}'
                .format(response.status_code))
        data = response.json()['items']

        for item in data:
            print (item['data']['name'] + ' - ' + item['data']['creator_id'] - item['data']['user_id'])


        # iterate through events and print them
        #for item in response.json()['items']:
        #  print("Deal data:\n{}"
        #          .format(json.dumps(item['data'], indent=4)));
        #  if item['meta']['event_type'] == 'updated':
        #      print("Updated: {}"
        #          .format(item['meta']['previous'].keys()))
        #      print("Old values:\n{}".format(
        #          json.dumps(item['meta']['previous'], indent=4)));

        # check if we have reached the top of the stream
        onTop = response.json()['meta']['top']

        # prepare the position for the next request
        startingPosition = response.json()['meta']['position']

    #print ("Sleeping...")
    #time.sleep(5)

