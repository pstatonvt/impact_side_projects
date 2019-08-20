import csv
import os

fname = 'ornl_master_granule_sheet.csv'
fname2 = 'GRANULES_ORNL_BEDI.txt'

with open(fname, errors='ignore') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    next(reader)
    next(reader)
    next(reader)
    next(reader)
    next(reader)
    with open(fname2,'w') as f:
        for row in reader:
            print(row)
            tmp = row[0].split('-ORNL_DAAC')
            # print(tmp[0].split('(')[-1] + '-ORNL_DAAC')
            GID = tmp[0].split('(')[-1] + '-ORNL_DAAC'
            if 'Collection' not in GID and '_NRT)' not in GID and 'ML2OH)' not in GID:
                f.write(GID + '\n')
            else:
                print(row[0])
        print('Finished!')
            #print(tmp[1].split('(')[-1] + '-' + tmp[2][:-2])
            #f.write(tmp[1].split('(')[-1] + '-' + tmp[2][:-2])
