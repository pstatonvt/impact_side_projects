# Import libraries
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re

# Set the URL you want to webscrape from
url = 'https://n5eil01u.ecs.nsidc.org/ATLAS/ATL08.001/'

# Connect to the URL
response = requests.get(url)

# Parse HTML and save to BeautifulSoup object
shortname_container = []
soup = BeautifulSoup(response.text, "html.parser")
print(soup)
# for i in range(len(soup.findAll('a'))): #'a' tags are for links
#     one_a_tag = soup.findAll('a')[i]
#     link = one_a_tag['href']
#     print(re.findall('^([^\/]*)', link))
#     shortname_container.append((re.findall('^([^\/]*)', link))[0])
# print(shortname_container)
