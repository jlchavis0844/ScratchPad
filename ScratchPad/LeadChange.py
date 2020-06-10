import requests
import json
import time

# your oauth token
token = "5bbddd26f6610378ef1c848952fd461e5c60bf55d609699ec3b28eb571bb3da7"

# main poll loop - check for new events every 5 seconds
startingPosition = 'tail'
while True:
    # loop to recieve all pages of events since we checked last time
    onTop = False
    while not onTop:
        url = "https://api.getbase.com/v3/leads/stream"
        response = requests.get(url, params={'position': startingPosition}, headers={'Authorization':'Bearer {}'.format(token)})
        if response.status_code != 200:
            raise Exception('Request failed with {}'.format(response.status_code))
        print(response.json()['meta']['position'])
        # iterate through events and print them
        #print('Checking ' + str(len(response.json()['items'])) + ' items')
        for item in response.json()['items']:
            #http://marketplace.eclipse.org/marketplace-client-intro?mpc_install=1403812print(item['data']['id'])
            #print(item['meta']['event_type'])
            if item['meta']['event_type'] == 'updated':
                print("lead data:\n{}".format(json.dumps(item['meta'], indent=4)));
#             if item['meta']['event_type'] == 'updated':
#                 print("Updated: {}".format(item['meta']['previous'].keys()))
#                 print("Old values:\n{}".format(json.dumps(item['meta']['previous'], indent=4)));
# 
        # check if we have reached the top of the stream
        onTop = response.json()['meta']['top']
# 
        # prepare the position for the next request
        startingPosition = response.json()['meta']['position']
        #print('Trying ' + startingPosition)
    #print('Done')
    exit()
