'''
This program reads in a text file formatted as follows:
[Long Name] ([Short Name]) - [UMM Link]
<!> The text file must be named "input.txt" <!>

The code then scrapes the short name and produces another text file
named 'short_name_list.txt'

-P.S. 6/18/2018
'''

import re

input_file = open('input.txt', 'r')
output_file = open('scraper_output.txt', 'w')
for line in input_file:
    short_name = re.findall('\((\S+_\S+)\)', line)
    for value in short_name:
        output_file.write(value + '\n')
