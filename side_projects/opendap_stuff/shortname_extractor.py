# A Python script to extract each project from within a DAAC
# P.S. 4/16/19

# Import libraries
import requests
import urllib
import json

# Choose DAAC
#DAAC = 'LAADS'
api_url = 'https://cmr.earthdata.nasa.gov/search/collections.json?provider_id=LAADS&page_size=2000'
print(api_url)

# Set up JSON parser
list_container = []
set_container = set()
json_data = urllib.request.urlopen(api_url).read()
json_output = json.loads(json_data)
json_list = json_output['feed']['entry']
for entry in json_list:
    list_container.append(entry['short_name'])
    set_container.add((entry['short_name']))
# print(len(list_container))
# print(len(set_container))
print(set_container)
