import requests
import json
import csv

emvoliastika = set()
personId = "xxxxxxxxx"
authorization ='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

my_headers ={'Authorization': authorization}
with open('tkAttiki.csv', 'r', encoding="utf8") as TK: #  tkGreece.csv
    reader = csv.reader(TK)
    for row in reader:

        print("TK:" + row[0] + " perioxh " + row[2])
        response = requests.post("https://emvolio.gov.gr/app/api/CovidService/CV_User_NearCenters",
                                 data={"zipCode": row[0], "personId": personId}, headers=my_headers)
        if 'exceptionObject' not in response.json().keys():
            # print(response.json())
            centers = response.json().get('centers')
            if len(centers) > 0:
                print(response.json())
                for center in centers:
                    emvoliastika.add((center.get('name'), center.get('id'),center.get('tk'), response.json().get('startDate')))

            print(emvoliastika)
#
with open('emvoliastika.json', 'w', encoding="utf8") as fp:
    json.dump(list(emvoliastika), fp)
fp.close()

day = 26

from datetime import datetime
with open('emvoliastika.json', 'r', encoding="utf8") as fp:
    reader = json.load(fp)

    for key in reader:
        # print(key[1])
        # print(key[3])

        for i in range(0,6):
            response = requests.post("https://emvolio.gov.gr/app/api/CovidService/CV_TimeSlots_Free",
                                     data={"centerId": key[1], "personId": personId, "firstDoseDate": "null",
                                           "zoneNum": "null", "selectedDate": '2021-05-'+str(day+i)+'T00:00:00+03:00', "dose": "1",
                                           "requestRecommended": "true"}, headers=my_headers)
            if 'exceptionObject' not in response.json().keys():
                # print(response.json())
                if response.json()['doses'] ==2 and response.json()['timeslotsFree'][0]['percentAvailable'] > 0:
                    response2 = requests.post("https://emvolio.gov.gr/app/api/CovidService/CV_TimeSlots_Free",
                                             data={"centerId": key[1], "personId": personId,
                                                   "firstDoseDate": response.json()['timeslotsFree'][0]['onDate'],
                                                   "zoneNum": "null", "selectedDate": "2021-05-29T21:00:00.000Z",
                                                   "dose": "2", "requestRecommended": "true"}, headers=my_headers)
                    date_time_0 = datetime.strptime(response.json()['timeslotsFree'][0]['onDate'], '%Y-%m-%dT%H:%M:%S+03:00')
                    date_time_1 = datetime.strptime(response2.json()['timeslotsFree'][0]['onDate'], '%Y-%m-%dT%H:%M:%S+03:00')

                    delta = date_time_1 - date_time_0
                    # get the vaccination centers that the available days between the shots is less than 50 (ie non Astra Zeneca)
                    if (delta.days < 50):
                        print(key)
                        print(delta.days)
                break

