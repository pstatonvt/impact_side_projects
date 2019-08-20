'''
A URL checker for ECHO10 collection-level XML formatted data. Checks for broken links in the following fields:
Description, DOI, CitationForExternalPublication, Online Access, Online Resource

Required python packages: wget, requests
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
#print("==========================================================================")
#print("| <!> Please enter your Earthdata Search username and password below <!> |")
#print("==========================================================================")
#username = input("Username: ")
#password = getpass.getpass()
print()
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
    CID = input("Enter a Concept ID: ")
    RIV = input("Enter a Revision ID: ")

    try:
        files = sorted(glob.glob('*.native'))
        for f in files:
            os.remove(f)
        print()
    except:
        pass

    # Concatenates all given information with base cmr web string and downloads the native file
    try:
        cmr_ping = 'https://cmr.earthdata.nasa.gov:443/search/concepts/' + CID + '/' + RIV + '.native'
        native = wget.download(cmr_ping)
        print()
        print("Downloaded " + cmr_ping + "!")
        print()
    except:
        print()
        print("======================================================")
        print("| This collection is no longer valid! Exiting now... |")
        print("======================================================")
        exit()

    # Check response from website and decode
    data = urllib.request.urlopen(cmr_ping).read()
    decode = data.decode()
    tree = ET.fromstring(data)

    # XML parsing - checking for links in description
    des_finder = tree.findall('Description')
    if len(des_finder) > 0:
        des = des_finder[0].text
        des_links = re.findall('(?:ht|f)tps?:[\S]*\/?\w+', des)
        for i in des_links:
            if i.startswith('ftp'):
                http.append(i)
                des_links.remove(i)

    # Ping description links
        for i in des_links:
            try:
                r1 = s.get(i, stream=True)
                request = s.get(r1.url, stream=True)
                #request = requests.get(i)
            except requests.exceptions.ConnectionError as e:
                broken.append(i + ' <--- <Description>')
                continue
            except requests.exceptions.MissingSchema as M:
                check.append(i + ' <--- <Description>')
                continue
            if request.status_code == 200:
                if request.status_code == 200 and not i.startswith('https://'):
                    http.append(i + ' <--- <Description>')
                else:
                    pass
            elif request.status_code < 400 and request.status_code >= 300:
                check.append(i + ' <--- <Description>')
            elif request.status_code >= 400:
                broken.append(i + ' <--- <Description>')
            else:
                check.append(i + ' <--- <Description>')
    else:
        print()
        print("*<!>* Consider adding a DOI for this collection if it exists. *<!>*")
        print()
        pass

    # XML parsing - find DOI link
    doi_finder = tree.findall('DOI/DOI')
    if len(doi_finder) > 0:
        doi_url = 'https://doi.org/' + doi_finder[0].text

    # Ping DOI link
        r1 = s.get(doi_url, stream=True)
        request = s.get(r1.url, stream=True)
        #request = requests.get(doi_url)
        if request.status_code == 200:
            if request.status_code == 200 and not doi_url.startswith('https://'):
                http.append(doi_url + ' <--- <DOI>')
            else:
                pass
        elif request.status_code < 400 and request.status_code >= 300:
            check.append(doi_url + ' <--- <DOI>')
        elif request.status_code >= 400:
            broken.append(i + ' <--- <DOI>')
        else:
            check.append(doi_url + ' <--- <DOI>')
    else:
        print()
        print("*<!>* Consider adding a DOI for this collection if it exists. *<!>*")
        print()
        pass

    # XML parsing - finding CitationForExternalPublication
    citation_finder = tree.findall('CitationForExternalPublication')
    if len(citation_finder) > 0:
        cit = citation_finder[0].text
        cit_links = re.findall('(?:ht|f)tps?:[\S]*\/(?:\w+(?:\.\w+)?)?', cit)
        for i in cit_links:
            if i.startswith('ftp'):
                http.append(i)
                cit_links.remove(i)

    # Ping CitationForExternalPublication links
        for i in cit_links:
            try:
                r1 = s.get(i, stream=True)
                request = s.get(r1.url, stream=True)
                #request = requests.get(i)
            except requests.exceptions.ConnectionError as e:
                broken.append(i + ' <--- <CitationForExternalPublication>')
                continue
            except requests.exceptions.MissingSchema as M:
                check.append(i + ' <--- <CitationForExternalPublication>')
                continue
            if request.status_code == 200:
                if request.status_code == 200 and not i.startswith('https://'):
                    http.append(i + ' <--- <CitationForExternalPublication>')
                else:
                    pass
            elif request.status_code < 400 and request.status_code >= 300:
                check.append(i + ' <--- <CitationForExternalPublication>')
            elif request.status_code >= 400:
                broken.append(i + ' <--- <CitationForExternalPublication>')
            else:
                check.append(i + ' <--- <CitationForExternalPublication>')
    else:
        pass

    # XML parsing - finding OnlineAccessURL
    OnlAcc_finder = tree.findall('OnlineAccessURLs/OnlineAccessURL')
    if len(OnlAcc_finder) > 0:
        OnlAcc_repo = []
        for i in OnlAcc_finder:
            OnlAcc_URL = i.find('URL').text
            OnlAcc_repo.append(OnlAcc_URL)
        for i in OnlAcc_repo:
            if i.startswith('ftp'):
                http.append(i)
                OnlAcc_repo.remove(i)

    # Ping OnlineAccessURL
        for i in OnlAcc_repo:
            try:
                r1 = s.get(i, stream=True)
                request = s.get(r1.url, stream=True)
                #request = requests.get(i)
            except requests.exceptions.ConnectionError as e:
                broken.append(i + ' <--- <OnlineAccessURLs>')
                continue
            except requests.exceptions.MissingSchema as M:
                check.append(i + ' <--- <OnlineAccessURLs>')
                continue
            if request.status_code == 200:
                if request.status_code == 200 and not i.startswith('https://'):
                    http.append(i + ' <--- <OnlineAccessURLs>')
                else:
                    pass
            elif request.status_code < 400 and request.status_code >= 300:
                check.append(i + ' <--- <OnlineAccessURLs>')
            elif request.status_code >= 400:
                broken.append(i + ' <--- <OnlineAccessURLs>')
            else:
                check.append(i + ' <--- <OnlineAccessURLs>')
    else:
        print()
        print("*<!>* Consider adding Online Access URLs for this collection if they exist. *<!>*")
        print()
        pass

    # XML parsing - finding OnlineResourceURLs
    OnlRes_finder = tree.findall('OnlineResources/OnlineResource')
    if len(OnlRes_finder) > 0:
        OnlRes_repo = []
        for i in OnlRes_finder:
            OnlRes_URL = i.find('URL').text
            OnlRes_repo.append(OnlRes_URL)
        for i in OnlRes_repo:
            if i.startswith('ftp'):
                http.append(i)
                OnlRes_repo.remove(i)

    # Ping OnlineResourceURL
        for i in OnlRes_repo:
            try:
                r1 = s.get(i, stream=True)
                request = s.get(r1.url, stream=True)
                #request = requests.get(i)
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
                    pass
            elif request.status_code < 400 and request.status_code >= 300:
                check.append(i + ' <--- <OnlineResources>')
            elif request.status_code >= 400:
                broken.append(i + ' <--- <OnlineResources>')
            else:
                check.append(i + ' <--- <OnlineResources>')
    else:
        print()
        print("*<!>* Consider adding access to Online Resources for this collection if they exist. *<!>*")
        print()
        pass

    # Final statements / error statements
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
    print("===============================================")
    print("| Would you like to open this file now? (Y/N) |")
    print("===============================================")
    opener = input("Enter your choice here: ").upper()
    if opener == 'Y':
        os.system("start " + native)
        print(" == Restarting the program ==")
        print()
        continue
    else:
        print("== Okay no problem :) Restarting program ==")
        print()
        continue
