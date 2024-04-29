import requests
import logging
import re
import json
import http.client as http_client
from datetime import datetime


class Appointment:
    def __init__(self, date_time, unit, duration, link):
        self.date_time: datetime = date_time
        self.unit = unit
        self.duration = duration
        self.link = link

    def __str__(self):
        return f"Date: {self.date_time}, Unit: {self.unit}, Duration: {self.duration} minutes"

    # Parse from json
    @staticmethod
    def from_json(json_data):
        return Appointment(datetime.fromisoformat(json_data["datetime_iso86001"]), json_data["unit"],
                           json_data["duration"], json_data["link"])


def enable_debug():
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def get_appointments() -> list[Appointment]:
    domain = "https://termine.bonn.de"
    response = requests.get(domain + "/m/dlz/extern/calendar/?uid=b91bb67b-15cf-44df-ab0b-96ebe25c1ae3",
                            allow_redirects=False)
    # Base url should return 302 with 'wsid' as a parameter in the url
    if response.status_code != 302:
        print("Couldn't get wsid token")
        exit()

    # Get parameter from the url
    base_url = domain + response.headers["Location"]
    # Only send cookies "__RequestVerificationToken" and "ASP.NET_SessionId"
    cookies = {
        "__RequestVerificationToken": response.cookies.get_dict()["__RequestVerificationToken"],
        "ASP.NET_SessionId": response.cookies.get_dict()["ASP.NET_SessionId"],
    }

    response2 = requests.get(base_url, cookies=cookies, allow_redirects=False)

    # Load request token
    pattern = (r"^(?:.*)<input type='hidden' id='RequestVerificationToken' name='__RequestVerificationToken' value='("
               r".*?)' />")
    match = re.search(pattern, response2.text, flags=re.MULTILINE)
    if match:
        form_token = match.group(1)
    else:
        print("Couldn't get form token")
        exit()

    # Load form data file
    form_data = open("form-data.txt", "r")
    form_data = form_data.read()
    form_data = "__RequestVerificationToken=" + form_token + form_data

    # Send post to base_url with form_data
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    requests.post(base_url, data=form_data, cookies=cookies, headers=headers, allow_redirects=False)

    # Finally, get the appointments
    url = base_url.split("?")[0] + "search_result?search_mode=earliest&" + base_url.split("?")[1]
    response4 = requests.get(url, cookies=cookies, allow_redirects=False)

    pattern = r"(?<=<div id=\"json_appointment_list\">).*?(?=</div>)"
    match = re.search(pattern, response4.text, flags=re.DOTALL)

    if match:
        appointments_json = json.loads(match.group(0))
        appointments = []
        for appointment in appointments_json["appointments"]:
            appointments.append(Appointment.from_json(appointment))
        return appointments
    else:
        print("JSON data not found")
        exit()
