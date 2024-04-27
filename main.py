import requests
import logging
import re
import json


# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.

def enable_debug():
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def get_appointments():
    # Request base url

    base_url = "https://termine.bonn.de/m/dlz/extern/calendar/?uid=b91bb67b-15cf-44df-ab0b-96ebe25c1ae3"
    # Headers
    light_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Host": "termine.bonn.de",
        "Origin": base_url,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-CA;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
    }

    response = requests.get(base_url, headers=light_headers, allow_redirects=False)
    # Base url should return 302 with 'wsid' as a parameter in the url
    # urllib automatically goes to 302 location

    if response.status_code != 302:
        print("Base url did not return 302")
        exit()
    print("Got correct 302")

    # Get parameter from the url
    base_url = "https://termine.bonn.de" + response.headers["Location"]
    cookie_token = response.cookies.get_dict()["__RequestVerificationToken"]

    # Only send cookies "__RequestVerificationToken" and "ASP.NET_SessionId"
    cookies = {
        "__RequestVerificationToken": cookie_token,
        "ASP.NET_SessionId": response.cookies.get_dict()["ASP.NET_SessionId"],
    }

    response2 = requests.get(base_url, cookies=cookies, headers=light_headers, allow_redirects=False)

    # Load request token
    pattern = r"^(?:.*)<input type='hidden' id='RequestVerificationToken' name='__RequestVerificationToken' value='(.*?)' />"
    match = re.search(pattern, response2.text, flags=re.MULTILINE)

    if match:
        token = match.group(1)
        print("Request 2 contained matching token")
    else:
        print("String not found")
        exit()

    # Load form data file
    form_data = open("form-data.txt", "r")
    form_data = form_data.read()
    form_data = "__RequestVerificationToken=" + token + form_data

    # Send post to base_url with form_data

    headers = light_headers.copy()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    response3 = requests.post(base_url, data=form_data, cookies=cookies, headers=headers, allow_redirects=False)
    print("Response 3 success: ", response3.status_code)

    # Finally, get the appointments

    url = base_url.split("?")[0] + "search_result?search_mode=earliest&" + base_url.split("?")[1]
    response4 = requests.get(url, cookies=cookies, headers=light_headers, allow_redirects=False)

    pattern = r"(?<=<div id=\"json_appointment_list\">).*?(?=</div>)"

    match = re.search(pattern, response4.text, flags=re.DOTALL)

    if match:
        json_data = match.group(0)
        # Now you can parse the JSON data using the json module
        appointments = json.loads(json_data)
        return appointments
    else:
        print("JSON data not found")
        exit()


if __name__ == "__main__":
    appointments = get_appointments()
    print(appointments)