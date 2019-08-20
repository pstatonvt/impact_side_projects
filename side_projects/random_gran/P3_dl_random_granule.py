#!/usr/bin/env python
# Author: Jeanne' le Roux
# Date: 2016-04-08  12:46:03
# Last Modified Time: 2016-04-08  13:28:42
# Requirements: pyCMR

## NEEDS TO BE RUN IN PYTHON 2 ##
import pyCMR
import sys
from random import randint

granules = pyCMR.searchGranule(limit=100, short_name='SoilSCAPE_1339', version='1')

l = str(len(granules))
print('Number of granules for this collection: ' + l)

L = int(l) - 1
print('Downloading random granule: ')
random = (randint(0, L))
print(random)

granules[random].download()
print(' Download complete.')
