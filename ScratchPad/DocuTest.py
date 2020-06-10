import requests
import json

from datetime import date
from datetime import datetime
from dateutil import tz
from pathlib import Path

ACCESS_TOKEN = "5bbddd26f6610378ef1c848952fd461e5c60bf55d609699ec3b28eb571bb3da7"
response = requests.get(
    url='https://api.getbase.com/v3/documents/stream?position=tail',
    headers={
      'Accept': 'application/json',
      'Authorization': 'Bearer ' + ACCESS_TOKEN
    },
    verify=True
  )

#print(response.text)
response_json = json.loads(response.text)
to_zone = tz.gettz('America/Pacific')
today = datetime.date.today().astimezone(to_zone)

createdDocs = []
top = False

while top == False:
    items = response_json['items']
    
    print(json.dumps(response_json, indent=4))
    
    for item in items:
        #date = dateutil.parser.parse(item['data']['created_at'])
        dateStr = str(item['data']['created_at'])[:10]
        date = datetime.strptime(dateStr, '%y-%m-%d').astimezone(to_zone)
        if date >= today and item['meta']['event_type'] == 'created':
            createdDocs.append(item['data']['id'])
            print('Adding ' + str(item['data']['id']))
    
    nextURI = response_json["meta"]["links"]["next"]
    top = response_json['meta']['top']
    response = requests.get(
    url=nextURI,
    headers={
      'Accept': 'application/json',
      'Authorization': 'Bearer ' + ACCESS_TOKEN
    },
    verify=True)
    response_json = json.loads(response.text)

for doc in createdDocs:
    fileName = 'unmatched.pdf'
    
    response = requests.get(
    url='https://api.getbase.com/v2/documents/' + str(doc),
    headers={
      'Accept': 'application/json',
      'Authorization': 'Bearer ' + ACCESS_TOKEN
    },
    verify=True)
    response_json = json.loads(response.text)
    
    try:
        if response_json['data']['resource_type'] == 'deal':
            resource = requests.get(
            url='https://api.getbase.com/v2/deals/' + str(response_json['data']['resource_id']),
            headers={
              'Accept': 'application/json',
              'Authorization': 'Bearer ' + ACCESS_TOKEN
            },
            verify=True)
            resource_json = json.loads(resource.text)
            fileName = response_json['data']['name'] + '-' + resource_json['data']['name'] + ".pdf"
            
        url = response_json['data']['download_url']
        file = Path(fileName)
        response = requests.get(url)
        file.write_bytes(response.content)
    except:
        print('Could not fetch the data. Deleted??')
        print()
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    