'''
Copyright 2016, United States Government, as represented by the Administrator of
the National Aeronautics and Space Administration. All rights reserved.
The "pyCMR" platform is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may obtain a
copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.
'''

import csv
import urllib.request
import ssl
import requests
from CheckerCollection import checkerRules
from CSVCollection import CollectionOutputCSVBackup
from JsonCollection import CollectionOutputJSON

class Checker():

    def fetchAllSciKeyWords(self):
        print("Fetch all Science Keywords ...")
        SciKeyWords = [[], [], [], [], [], [], []]
        # SciCategoryKeys, SciTopicKeys, SciTermKeys, SciVarL1Keys, SciVarL2Keys, SciVarL3Keys, SciDetailVar
        response = requests.get(self.urls['ScienceKeywordURL']).text.split('\n')
        data = csv.reader(response, delimiter=',')
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            SciKeyWords[0] += item[0:1]
            SciKeyWords[1] += item[1:2]
            SciKeyWords[2] += item[2:3]
            SciKeyWords[3] += item[3:4]
            SciKeyWords[4] += item[4:5]
            SciKeyWords[5] += item[5:6]
            SciKeyWords[6] += item[6:7]
        for i in range(7):
            SciKeyWords[i] = list(set(SciKeyWords[i]))
        return SciKeyWords

    def fetchAllPlatforms(self):
        print("Fetch all Platforms ...")
        Platforms = [[], [], [], []]
        # Category, Series_Entity, Short_Name, Long_Name
        response = requests.get(self.urls['PlatformURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            Platforms[0] += item[0:1]
            Platforms[1] += item[1:2]
            Platforms[2] += item[2:3]
            Platforms[3] += item[3:4]
        for i in range(4):
            Platforms[i] = list(set(Platforms[i]))
        return Platforms

    def fetchAllInstrs(self):
        print("Fetch all Instruments ...")
        InstrKeyWords = [[], [], [], [], [], []]
        # Category, SciTopicKeys, SciTermKeys, SciVarL1Keys, SciVarL2Keys, SciVarL3Keys, SciDetailVar
        response = requests.get(self.urls['InstrumentURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            InstrKeyWords[0] += item[0:1]
            InstrKeyWords[1] += item[1:2]
            InstrKeyWords[2] += item[2:3]
            InstrKeyWords[3] += item[3:4]
            InstrKeyWords[4] += item[4:5]
            InstrKeyWords[5] += item[5:6]
        for i in range(6):
            InstrKeyWords[i] = list(set(InstrKeyWords[i]))
        return InstrKeyWords

    def fetchAllEnums(self):
        print("Fetch all UMM Enum Lists ...")
        test = requests.get(url=self.urls['UMMURL'])
        defs = test.json()['definitions']
        tags = defs.keys()
        self.enums = {}

        for tag in tags:
            if tag.endswith('Enum'):
                self.enums[tag] = defs[tag]['enum']
        self.enums['CollectionProgressEnum'] = ['IN WORK','PLANNED','COMPLETE']
        self.enums['CollectionDataTypeEnum'] = ['NEAR_REAL_TIME','SCIENCE_QUALITY','OTHER']
        self.enums['ProcessingLevelIDEnum'] = ["0","1A","1B","2","3","4"]

    def __init__(self, UMMversion):
        self.urls = {}

        self.urls['LocationKeywordURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/locations/locations.csv"
        self.urls['ScienceKeywordURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/sciencekeywords/sciencekeywords.csv"
        self.urls['ArchiveCenterURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv"
        self.urls['PlatformURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/platforms/platforms.csv"
        self.urls['InstrumentURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/instruments/instruments.csv"
        self.urls['ProjectURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/projects/projects.csv"
        self.urls['ResourcesTypeURL'] = "https://gcmdservices.gsfc.nasa.gov/static/kms/rucontenttype/rucontenttype.csv"
        self.urls['ArchtoURLs'] = {'SEDAC': 'http://sedac.ciesin.columbia.edu/data/set/',
                              'GHRC': 'https://fcportal.nsstc.nasa.gov/pub',
                              'NSIDC': 'http://nsidc.org/data/',
                              'LPDAAC': 'https://lpdaac.usgs.gov/node/',
                              'ORNL_DAAC': 'http://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id',
                              'OB.DAAC': 'http://oceandata.sci.gsfc.nasa.gov/',
                              'Alaska Satellite Facility': 'https://vertex.daac.asf.alaska.edu/'}
        self.urls['UMMURL'] = ("https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/raw/collection/v" +
              UMMversion + "/umm-cmn-json-schema.json")
        self.fetchAllEnums()
        self.checkerRules = checkerRules(self.urls,self.enums)
        # self.collectionOutputCSV = CollectionOutputCSV(self.checkerRules, self.fetchAllPlatforms, self.fetchAllInstrs,
        #                                                self.fetchAllSciKeyWords)
        self.collectionOutputJSON = CollectionOutputJSON(self.checkerRules, self.fetchAllPlatforms, self.fetchAllInstrs,
                                                         self.fetchAllSciKeyWords)

    def checkAll(self, metadata,titles,cid):
        return self.collectionOutputJSON.checkAll(metadata,titles,cid)

    def checkAllJSON(self, metadata,titles,cid):
        return self.collectionOutputJSON.checkAll(metadata,titles,cid)
