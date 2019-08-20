'''
A URL checker for ECHO 10 granule-level XML formatted data.  Checks for broken links in the following fields:
Online Access, Online Resource

Required python packages: wget, requests

Windows Key -> "cmd" -> Enter Key -> "pip install --user wget"
Windows Key -> "cmd" -> Enter Key -> "pip install --user requests"
'''

import urllib.request, urllib.error
import ssl
import xml.etree.ElementTree as ET
import re
from urllib.request import Request, urlopen
import wget
import os
import glob
import requests
import subprocess
import getpass

# Earthdata Login Info
s = requests.Session()
# print("==========================================================================")
# print("| <!> Please enter your Earthdata Search username and password below <!> |")
# print("==========================================================================")
# username = input("Username: ")
# password = getpass.getpass()
# print()
s.auth = ('pstaton', 'Pts56822!')

while True:


    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Construct repos for URL errors
    broken = []
    http = []
    check = []

    # Ask user to provide collection and revision IDs
    CID = input("Enter a Granule Concept ID: ")

    try:
        files = sorted(glob.glob('./G*'))
        for f in files:
            os.remove(f)
    except:
        pass


    # Concatenates all given information with base cmr web string and downloads the native file
    cmr_ping = 'https://cmr.earthdata.nasa.gov:443/search/concepts/' + CID
    native = wget.download(cmr_ping)
    print()
    print("Downloaded " + cmr_ping + "!")
    print()

    # Check response from website and decode
    data = urllib.request.urlopen(cmr_ping).read()
    decode = data.decode()
    tree = ET.fromstring(data)


    # XML parsing - find OnlineAccessURL
    OnlAcc_finder = tree.findall('OnlineAccessURLs/OnlineAccessURL')
    OnlAcc_repo = []
    for i in OnlAcc_finder:
        OnlAcc_URL = i.find('URL').text
        OnlAcc_repo.append(OnlAcc_URL)
    if len(OnlAcc_repo) < 1:
        print()
        print("*<!>* No OnlineAccessURL Provided! *<!>*")
        print()
    for i in OnlAcc_repo:
        if i.startswith('ftp'):
            http.append(i)
            OnlAcc_repo.remove(i)

    # Ping OnlineAccessURL
    if len(OnlAcc_repo) > 0:
        for i in OnlAcc_repo:
            try:
                r1 = s.get(i, stream=True)
                request = s.get(r1.url, stream=True)
                #request = requests.get(i, timeout = 2)
            except requests.exceptions.ConnectionError as e:
                broken.append(i + ' <--- <OnlineAccessURLs>')
                continue
            if request.status_code == 200:
                if request.status_code == 200 and not i.startswith('https://'):
                    http.append(i + ' <--- <OnlineAccessURLs>')
                else:
                    #print("HTTPS Success:", i)
                    pass
            elif request.status_code < 400 and request.status_code >= 300:
                check.append(i + ' <--- <OnlineAccessURLs>')
                #print("Error code", request.status_code, "on link:", i)
            else:
                broken.append(i + ' <--- <OnlineAccessURLs>')
    else:
        pass

    # XML parsing - finding OnlineResourceURLs
    OnlRes_finder = tree.findall('OnlineResources/OnlineResource')
    OnlRes_repo = []
    for i in OnlRes_finder:
        OnlRes_URL = i.find('URL').text
        OnlRes_repo.append(OnlRes_URL)
    if len(OnlRes_repo) < 1:
        print()
        print("*<!>* No OnlineResourceURL Provided! *<!>*")
        print()
    for i in OnlRes_repo:
        if i.startswith('ftp'):
            http.append(i)
            OnlRes_repo.remove(i)

    # Ping OnlineResourceURL
    if len(OnlRes_repo) > 0:
        for i in OnlRes_repo:
            try:
                r1 = s.request('head', i)
                request = s.head(r1.url, auth=s.auth)
                #request = requests.get(i, timeout = 2)
            except requests.exceptions.ConnectionError as e:
                broken.append(i + ' <--- <OnlineResources>')
                continue
            except requests.exceptions.MissingSchema as M:
                check.append(i + ' <--- <OnlineResources>')
                continue
            if request.status_code == 200:
                if request.status_code == 200 and not i.startswith('https://'):
                    http.append(i + ' <--- <OnlineResources>')
                else:
                    #print("HTTPS Success:", i)
                    pass
            elif request.status_code < 400 and request.status_code >= 300:
                check.append(i + ' <--- <OnlineResources>')
                #print("Error code", request.status_code, "on link:", i)
            else:
                broken.append(i + ' <--- <OnlineResources>')
    else:
        pass

    print("=== Recommend changing the URLs listed below to 'https://' ===")
    if len(http) == 0:
        print("No links to check here :)")
    else:
        for i, value in enumerate(http, 1):
            print(i, value)
    print()

    print("=== The links below appear to be broken. ===")
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

    print()
    print("===============================================")
    print("| Would you like to open this file now? (Y/N) |")
    print("===============================================")
    opener = input("Enter your choice here: ").upper()
    if opener == 'Y':
        os.system("start " + native)
        print()
        continue
    else:
        print("Okay no problem :) Restarting program...")
        print()
        continue
