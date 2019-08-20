'''
A program that tests the health of URLs either within a 'master' json file,
or a CSV file. At the start of the program, the user can either select
'JSON' or 'CSV' (not case sensitive), and the program will begin to ping
the URLs within the chosen file.

<!> [STRICT FILE NAMES REQURED!] <!>
The JSON file must be named, 'cdi_master.json', and the CSV file must
be named 'csv_report.csv'.

12/4/2018 P.S.
'''

# Import required packages
import requests
import os.path
import json
import csv
import time

file_type = input('Choose a file type (JSON/CSV): ')

if file_type.upper() == "JSON":
    print('\'JSON\' chosen! Reading [cdi_master.json] now...\n')
    # Check if correct text files exist in current directory
    with open('cdi_master.json', 'r') as json_info:
        master_json = json.load(json_info)
    if not os.path.exists('bad_links.txt') or not os.path.exists('good_links.txt'):
        bad_links_file = open('bad_links.txt', 'w')
        good_links_file = open('good_links.txt', 'w')
    else:
        bad_links_file = open('bad_links.txt', 'w')
        good_links_file = open('good_links.txt', 'w')
    # Begin link checking and writing to respective output files
    counter = 0
    for line in master_json:
        counter += 1
        if counter % 50 == 0:
            print('On collection ' + str(line['cdi_id']) + ' out of ' + str(len(master_json)) + '...')
        if counter % 5 == 0:
            time.sleep(0.5)
        if not line['catalog_url']:
            print('<Skipping collection ' + str(counter) + ' due to an empty Catalog URL!>')
        elif requests.get(line['catalog_url'], allow_redirects=False).status_code == 200:
            good_links_file.write(str(line['cdi_id']) + ' | '+ line['catalog_url'] + '\n')
        else:
            bad_links_file.write(str(line['cdi_id']) + ' | '+ line['catalog_url'] + '\n')
    print('<!> [COMPLETE] <!>')

elif file_type.upper() == "CSV":
    bad_links = []
    csv_file = open('csv_report.csv')
    csv_reader = csv.reader(csv_file)
    print('Double checking to make sure all links are healthy...\n')
    next(csv_reader)
    counter = 0
    for row in csv_reader:
        if counter % 5 == 0:
            time.sleep(0.5)
        if requests.get(row[0], allow_redirects=False).status_code == 200:
            counter += 1
        else:
            print('<!> Check this link: <!> ', row[0])
    if counter > 0:
        print('All links appear to be healthy! The CSV is ready to be shipped! :)')

else:
    print('<!> Input Error <!>')
    print('<!> Exiting now... <!>')
    exit()
