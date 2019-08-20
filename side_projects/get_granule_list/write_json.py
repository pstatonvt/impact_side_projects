import requests
import xml.etree.ElementTree as ET
import urllib.request
import json
import datetime
then = datetime.datetime.now()

base_api_url = 'https://cmr.earthdata.nasa.gov/search/concepts/'

daac = 'ORNL_DAAC'

reviewed_dict = {}


with open('GRANULES_ORNL_BEDI.txt','r') as f:
    GranuleIDs = f.read().splitlines()

for GranuleID in GranuleIDs:
    api_hits = urllib.request.urlopen('https://cmr.earthdata.nasa.gov/search/granules?concept_id=' + GranuleID)
    e = ET.parse(api_hits)
    tree = ET.ElementTree(e)
    root = tree.getroot()
    hits = int(root.find('.//hits').text)
    if hits != 0:
        api_url = base_api_url + GranuleID + '.json'
        api = requests.get(url=api_url)
        CollectionID = api.json().get('collection_concept_id')
        reviewed_dict[CollectionID] = GranuleID

    else:
        pass

url = 'https://cmr.earthdata.nasa.gov/search/collections.json?tag_key=gov.nasa.eosdis&provider_id=' + daac + '&page_size=1&page_num=1&include_facets=true'

project_list = []

api = requests.get(url=url)
#loop through each of the collections to get the data center
fields = api.json()['feed']['facets']
#find the location of the project field in the facets dictionary and extract the values-counts
projects = next(item for item in fields if item.get("field") == "project").get('value-counts')
#take the project name from each list and append it to our existing project_list list
project_list.extend([item[0] for item in projects])

GES_DISC_dict = {}

for project in sorted(project_list):
    proj = project.replace(' ', '%20')
    url = 'https://cmr.earthdata.nasa.gov/search/collections?provider_id=' + daac  + '&project=' + proj + '&page_size=2000'
    api = urllib.request.urlopen(url)
    e = ET.parse(api)
    tree = ET.ElementTree(e)
    root = tree.getroot()
    CollectionIDs = root.findall('.//id')
    GES_DISC_dict[project] = {}
    for CollectionID in CollectionIDs:
        if not reviewed_dict.get(CollectionID.text):
            #Query the API based on the DAAC and the page size provided
            url = 'https://cmr.earthdata.nasa.gov/search/granules?concept_id=' + CollectionID.text
            # retrieve the xml from the API using the urllib library
            api = urllib.request.urlopen(url)
            #parse the xml file using the xml library
            e = ET.parse(api)
            #retrieve the structure of the xml file
            tree = ET.ElementTree(e)
            root = tree.getroot()
            hits = int(root.find('.//hits').text)
            if CollectionID.text == 'C1000000064-ORNL_DAAC':
                print(CollectionID.text, hits)
            if hits > 0:
                #find all of the concept ids, entry titles, and cmr locations of each collection in the XML
                location = root.find('.//location').text
                revisionid = root.find('.//revision-id').text
                granuleid = location.split('/')[-2]
                if CollectionID.text == 'C1000000064-ORNL_DAAC':
                    print(location,revisionid,granuleid)
                GES_DISC_dict[project][CollectionID.text] = {'granule_concept_id': granuleid,'granule_revision_id': revisionid ,'original_concept_id': granuleid,'original_revision_id': revisionid}
            else:
                GES_DISC_dict[project][CollectionID.text] = {'granule_concept_id': None,'granule_revision_id': None,'original_concept_id': None,'original_revision_id': None}
        else:
            print('in the else', reviewed_dict.get(CollectionID.text))
            granuleid = reviewed_dict.get(CollectionID.text)
            #Query the API based on the DAAC and the page size provided
            url = 'https://cmr.earthdata.nasa.gov/search/granules?concept_id=' + CollectionID.text
            # retrieve the xml from the API using the urllib library
            api = urllib.request.urlopen(url)
            #parse the xml file using the xml library
            e = ET.parse(api)
            #retrieve the structure of the xml file
            tree = ET.ElementTree(e)
            root = tree.getroot()
            #find all of the concept ids, entry titles, and cmr locations of each collection in the XML
            revisionid = root.find('.//revision-id').text
            GES_DISC_dict[project][CollectionID.text] = {'granule_concept_id': granuleid, 'granule_revision_id': revisionid, 'original_concept_id': granuleid, 'original_revision_id': revisionid}


with open('GES_DISC_summary.json','w') as jsonfile:
    json.dump(GES_DISC_dict,jsonfile)

now = datetime.datetime.now()

print(now - then)
