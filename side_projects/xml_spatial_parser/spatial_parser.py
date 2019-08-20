'''
A Python script to parse through an XML creating columns for North,
South, West, and East bounding coordinates from an XML file.
-P.S. 6/5/19
'''

# Import libraries
import xml.etree.ElementTree as ET
import requests
import urllib

# Create and setup CSV file with titled columns
csv = open('LS7_bounding_boxes_page2.csv', 'w')
csv_output = 'LS2_bounding_boxes_page2.csv'
column_title_row = 'South Bounding, West Bounding, North Bounding, East Bounding\n'
csv.write(column_title_row)

# Set up XML/JSON parse
api_url = 'https://maap-project.org/search/granules.json?short_name=Landsat7_SurfaceReflectance&version=1&page_num=2&page_size=2000'
# Had to force a JSON API call - reading from a local XML file wasn't working for some reason.
json_data = requests.get(api_url).json()
json_feed = (json_data.get('feed'))
json_entry_list = json_feed.get('entry')
# Loop through the JSON API call, getting "boxes" values and then convert to an indexible list
# Write values to corresponding columns in the CSV file
for box_entry in json_entry_list:
    bounding_box_list = (box_entry.get('boxes')[0]).split(' ')
    # south_bounding is bounding_box_list[0]
    # west_bounding is bounding_box_list[1]
    # north_bounding is bounding_box_list[2]
    # east_bounding is bounding_box_list[3]
    row = bounding_box_list[0] + ',' + bounding_box_list[1] + ',' + bounding_box_list[2] + ',' + bounding_box_list[3] + '\n'
    csv.write(row)
