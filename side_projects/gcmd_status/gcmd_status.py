import requests
from reprint import output
import time

SUCCESS_MESSAGE = "<ONLINE>"
FAILURE_MESSAGE = "<OFFLINE>"

gcmd = {
          'science_keywords': {
            'name': 'Science Keywords',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/sciencekeywords/sciencekeywords.csv?ed_wiki_keywords_page'
          },
          'providers': {
            'name': 'Providers',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv?ed_wiki_keywords_page'
          },
          'instruments': {
            'name': 'Instruments',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/instruments/instruments.csv?ed_wiki_keywords_page'
          },
          'platforms': {
            'name': 'Platforms',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/platforms/platforms.csv?ed_wiki_keywords_page'
          },
          'locations': {
            'name': 'Locations',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/locations/locations.csv?ed_wiki_keywords_page'
          },
          'horizontal_data': {
            'name': 'Horizontal Data Resolution',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/platforms/platforms.csv?ed_wiki_keywords_page'
          },
          'vertical_data': {
            'name': 'Vertical Data Resolution',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/verticalresolutionrange/verticalresolutionrange.csv?ed_wiki_keywords_page'
          },
          'temporal': {
            'name': 'Temporal Data Resolution',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/temporalresolutionrange/temporalresolutionrange.csv?ed_wiki_keywords_page'
          },
          'url_content': {
            'name': 'URL Content Type',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/rucontenttype/rucontenttype.csv?ed_wiki_keywords_page'
          },
          'chrono': {
            'name': 'Chronostratigraphic Units',
            'url': 'https://gcmdservices.gsfc.nasa.gov/static/kms/temporalresolutionrange/temporalresolutionrange.csv?ed_wiki_keywords_page'
          }
       }

while True:
    with output(output_type='dict') as output_lines:
        for gcmd_entry in gcmd:
            entry = gcmd[gcmd_entry]
            name = entry['name']
            message_string = SUCCESS_MESSAGE
            if requests.get(entry['url']).status_code != 200:
                message_string = FAILURE_MESSAGE
            output_lines[name] = message_string
    time.sleep(5)
