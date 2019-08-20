'''
A URL checker for UMM-JSON files
'''

import urllib.request, urllib.error
import ssl
import requests
import json
import getpass

# A function for checking URLs
def check_url(url):
    try:
        initial_response = session.get(url, stream=True)
        request = session.get(initial_response.url, stream=True)
    except requests.exceptions.ConnectionError as e:
        broken.append(url)
    except requests.exceptions.MissingSchema as M:
        check.append(url)
    if request.status_code == 200:
        if not url.startswith('https://'):
            http.append(url)
    elif request.status_code >= 400:
        broken.append(url)
    else:
        check.append(url)

# Earthdata Login Info
session = requests.Session()
print("==========================================================================")
print("| <!> Please enter your Earthdata Search username and password below <!> |")
print("==========================================================================")
username = input("Username: ")
print("<!> WARNING: You will not see your password being typed out <!>")
password = getpass.getpass()
print()
session.auth = (username, password)

while True:
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Construct repos for URL errors
    http = []
    broken = []
    check = []

    # Ask user to provide collection and revision IDs
    CID = input("Enter a Concept ID: ")
    RIV = input("Enter a Revision ID: ")

    # Concatenates all given information with base cmr web string and downloads the native file
    try:
        cmr_ping = 'https://cmr.earthdata.nasa.gov/search/concepts/' + CID + '/' + RIV + '.umm-json'

    except:
        print()
        print("======================================================")
        print("| This collection is no longer valid! Exiting now... |")
        print("======================================================")
        exit()

    # Check response from website and decode
    data = requests.get(url=cmr_ping).json()

    # Check <Abstract>
    # Currently there is not a check for abstract due to codec error

    # Check <DOI>/<DOI> link
    doi = data.get('DOI').get('DOI')
    doi_auth = 'https://dx.doi.org/'
    url = doi_auth + doi
    check_url(url)

    # Check <RelatedUrls>/<URL> links
    related_url = data.get('RelatedUrls')
    if not isinstance(related_url, list):
        related_url = [related_url]
    for item in related_url:
        check_url(item.get('URL'))

    # Check <AdditionalAttributes>/<Value>
    add_atts = data.get('AdditionalAttributes')
    if not isinstance(add_atts, list):
        add_atts = [add_atts]
    for item in add_atts:
        if (item.get('Value')) and (item.get('Value')).startswith('10.'):
            check_url(doi_auth+item.get('Value'))

    # Check <DataCenters>/<ContactInformation>/<RelatedUrls>/<URL> links
    data_centers = data.get('DataCenters')
    if not isinstance(data_centers, list):
        data_centers = [data_centers]
    for value in data_centers:
        dc_related_url = value.get('ContactInformation').get('RelatedUrls')
    if not isinstance(dc_related_url, list):
        dc_related_url = [dc_related_url]
    for value in dc_related_url:
        check_url(value.get('URL'))

    # Final statements / error statements
    print()
    print("=== Recommend changing the URLs listed below to 'https://' ===")
    if len(http) == 0:
        print("No links to check here :)")
    else:
        for i, value in enumerate(http, 1):
            print(i, value)
    print()

    print("=== The links below appear to be broken ===")
    if len(broken) == 0:
        print("No links to check here :)")
    else:
        for i, value in enumerate(broken, 1):
            print(i, value)
    print()

    print("=== Recommend double checking the links below  ===")
    if len(check) == 0:
        print("No links to check here :)")
    else:
        for i, value in enumerate(check, 1):
            print(i, value)
    print()
    print('<!> RESTARTING THE PROGRAM <!> ')
    print()
