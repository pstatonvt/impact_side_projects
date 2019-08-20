'''
A program to create a text file of short names and revision IDs
(organized by project) for each DAAC.

-P.S. 6/15/2018
'''

# Import tools
import requests
import urllib
import json
import os
import xml.etree.ElementTree as ET

# Asks user which DAAC they need and initializes output
print("Please choose a DAAC from the list below:")
print(['ORNL_DAAC','SEDAC','GHRC','GES_DISC','ASDC','OBDAAC','ASF','LAADS','NSIDC','LPDAAC','CDDIS','PODAAC'])
print()
daac = input("Enter here: ")
json_url = 'https://cmr.earthdata.nasa.gov/search/collections.json?provider_id=' + daac + '&page_size=2000'
xml_url = 'https://cmr.earthdata.nasa.gov/search/collections?provider_id=' + daac + '&page_size=2000'
json_data = requests.get(url=json_url).json()
xml_data = urllib.request.urlopen(xml_url).read()
tree = ET.fromstring(xml_data)

# Reads through API (JSON) finding 'Short Names'
# Writes output to a text file called '[daac]_shortname.txt'
shortname = open(daac + '_shortname.txt', 'w')
entry_list = json_data.get('feed').get('entry')
for value in entry_list:
    shortname.write(value.get('short_name') + '\n')

# Reads through API (XML) finding 'Revision IDs'
# Writes output to a text file called '[daac]_rev_id.txt'
reference_entry = tree.findall('references/reference')
rev_id = open(daac + '_rev_id.txt', 'w')
for value in reference_entry:
    rev_id.write(value.findall('revision-id')[0].text + '\n')

shortname.close()
rev_id.close()
print()
print('<!> Files created! <!>')
