'''
This script calls the data.gov carpark availability api at 1 hour intervals between the start date that you set (max 1 month in the past from now),
to today. It then records the utilisation percentage of each carpark and the timestamp in the output json. This process is carried out for all carparks
'''
import time
import requests
from datetime import datetime, timedelta
import json

import pytz

#start time
timestamp = "2021-04-13T08:30:00"

main_dict = {}

#escape counter
esc_counter = 0

# request api
while datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") < datetime.now():

    response = requests.get("https://api.data.gov.sg/v1/transport/carpark-availability", params={'date_time':timestamp})
    #get carpark
    try:
        if esc_counter <= 30:
            carpark_list = response.json()['items'][0]["carpark_data"]
        else:
            #move datetime 1 hour forward
            print(f"Failed:{timestamp}")
            updated_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=1)
            timestamp = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
            esc_counter = 0
            continue
    except:
        print(f"Retrying: {timestamp}")
        esc_counter += 1
        continue
    
    #reset counter on successfull api
    esc_counter = 0

    #iterate through all carparks
    for carpark in carpark_list:
    #available lots
        avail_lots = int(carpark["carpark_info"][0]["lots_available"])
        #all lots
        total_lots = int(carpark["carpark_info"][0]["total_lots"])
        #identifier number
        carpark_num = carpark["carpark_number"]
        #utilisation percentage
        if total_lots != 0:
            util_pct = 1 - round(avail_lots/total_lots, 3)
    
        if carpark_num not in main_dict:
            main_dict[carpark_num] = {'util_pct':[util_pct], 'timestamp':[timestamp]}
        else:
            main_dict[carpark_num]['util_pct'].append(util_pct)
            main_dict[carpark_num]['timestamp'].append(timestamp)
    
    #move datetime 1 hour forward
    updated_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=1)
    timestamp = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Completed:{timestamp}")

#store data on disk
with open('data/carpark_data.json', 'w') as f:
    json.dump(main_dict, f)