# A Python script to extract each project from within a DAAC
# P.S. 4/16/19

# Import libraries
import xml.etree.ElementTree as ET
import requests
import urllib
import json

# Choose DAAC
DAAC = 'LPDAAC_ECS'
api_url = 'https://cmr.earthdata.nasa.gov/search/collections?provider_id=' + DAAC + '&page_size=2000'
# api_url = 'https://cmr.earthdata.nasa.gov/search/collections?project=olympex&page_size=2000'

# Set up XML parser
xml_data = urllib.request.urlopen(api_url).read()
tree = ET.fromstring(xml_data)
xml_tag_list = tree.findall('references/reference')

# Loop through XML to form CID URL API calls
project_container = set()
for entry in xml_tag_list:
    location = entry.findall('location')[0].text
    json_url = location + '.umm-json'
    id = (entry.findall('id')[0].text)
    rev_id = (entry.findall('revision-id')[0].text)
    cid_url = 'https://cmr.earthdata.nasa.gov/search/concepts/' + id + '/' + rev_id + '.umm-json'\

    # Read as JSON to get Project Short Name
    json_data = requests.get(url=cid_url).json()
    try:
        projects_list = (json_data.get('Projects'))
        # print(projects_list)
        for project_entry in projects_list:
            project_container.add(project_entry.get('ShortName'))
    except:
        print('<!> EXCEPTION <!>')
        print('No Project found for: ' + cid_url)
print(project_container)
