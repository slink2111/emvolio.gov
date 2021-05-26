import requests
import json
import csv

emvoliastika = set()
# set the personId and authorization based on the session info you have with the https://emvolio.gov.gr, you can find them in the Web developer options of your browser 
# in the Network -> Requests and Header tabs
personId = "xxxxxxxxx"
authorization ='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

my_headers ={'Authorization': authorization}

# Here we get the list of vaccination centers based on the list of Postal codes in the csv file
# the tkAttiki.csv includes postal codes for Attica region 
# the tkGreece.csv includes the postal codes for all Greece
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
# we write the list of vaccination centers (name, id, postal code, start date in emvoliastika.json file
with open('emvoliastika.json', 'w', encoding="utf8") as fp:
    json.dump(list(emvoliastika), fp)
fp.close()


# We set the input criteria for the first vacination day we want to search, with day=26 we search for '2021-05-26' and on (line 53)
day = 26

from datetime import datetime

with open('emvoliastika.json', 'r', encoding="utf8") as fp:
    reader = json.load(fp)

    for key in reader:
        # print(key[1])
        # print(key[3])

        # because the start date might not be available, we search for a range of days after the start date (be carefull if month changes also)
        for i in range(0, 6):
            response = requests.post("https://emvolio.gov.gr/app/api/CovidService/CV_TimeSlots_Free",
                                     data={"centerId": key[1], "personId": personId, "firstDoseDate": "null",
                                           "zoneNum": "null",
                                           "selectedDate": '2021-05-' + str(day + i) + 'T00:00:00+03:00', "dose": "1",
                                           "requestRecommended": "true"}, headers=my_headers)
            if 'exceptionObject' not in response.json().keys():
                # print(response.json())
                for i, percent in enumerate(response.json()['timeslotsFree']):
                    if response.json()['timeslotsFree'][i]['percentAvailable'] > 0:
                        response2 = requests.post("https://emvolio.gov.gr/app/api/CovidService/CV_TimeSlots_Free",
                                                  data={"centerId": key[1], "personId": personId,
                                                        "firstDoseDate": response.json()['timeslotsFree'][i]['onDate'],
                                                        "zoneNum": "null", "selectedDate": "2021-05-29T21:00:00.000Z",
                                                        "dose": "2", "requestRecommended": "true"}, headers=my_headers)
                        # if we can get a start date we try to get a date for the second vaccination apointment
                        for j, percents in enumerate(response2.json()['timeslotsFree']):
                            if response2.json()['timeslotsFree'][j]['percentAvailable'] > 0:
                                date_time_0 = datetime.strptime(response.json()['timeslotsFree'][i]['onDate'],
                                                                '%Y-%m-%dT%H:%M:%S+03:00')
                                date_time_1 = datetime.strptime(response2.json()['timeslotsFree'][j]['onDate'],
                                                                '%Y-%m-%dT%H:%M:%S+03:00')

                                delta = date_time_1 - date_time_0
                                # we print the vaccination centers that the available days between the two possible apointments is less than 50 (ie POSSIBLE non Astra Zeneca)
                                if (delta.days < 50):
                                    print("Vaccination center: " + key[0] + " PK: " + key[2] + " available date of 1st vaccination " + response.json()['timeslotsFree'][i]['onDate'])
                                    print("Days between vaccination appointments " + delta.days)
                                    break
                        break
                break

