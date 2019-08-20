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

import json
import requests
import re
from Result import *
from xmlParser import XmlListConfig
from xmlParser import XmlDictConfig
from xml.etree import ElementTree

#Set up the urls for collection and granule level api queries.
# Note: page_size={} and page_num={} are initializing the urls and are formatted in the line
# requests.get(url.format(limit,pagenum) where pagenum is a calculated value.
granuleUrl = "https://cmr.earthdata.nasa.gov/search/granules?page_size={}&page_num={}"
granuleMetaUrl = "https://cmr.earthdata.nasa.gov/search/granules.echo10?page_size={}&page_num={}"
collectionUrl = "https://cmr.earthdata.nasa.gov/search/collections?page_size={}&page_num={}"
collectionMetaUrl = "https://cmr.earthdata.nasa.gov/search/collections.json?page_size={}&page_num={}"

def printHello():
    """
    A test function
    :return:
    """
    print("Hello World!")

def _searchResult(url, total, limit, **kwargs):
    """
    Search using the CMR apis
    :param url:
    :param total:
    :param limit:
    :param args:
    :param kwargs:
    :return: generator of xml strings
    """
    # Format the url with customized parameters
    for k, v in kwargs.items():
        url += "&{}={}".format(k, v)
    result = [requests.get(url.format(limit,pagenum)).text
              for pagenum in range(1, int((total - 1) / limit) + 2)]
    # for res in result:
    #     for ref in re.findall("<reference>(.*?)</reference>", res):
    #         yield ref
    return [ref for res in result
            for ref in re.findall("<reference>(.*?)</reference>", res)]

def searchGranule(total=1,limit=1, **kwargs):
    """
    Search the CMR granules
    :param total: the number of results desired
    :param limit: limit of the size of the page (2000 max)
    :param kwargs: search parameters
    :return: list of results (<Instance of Result>)
    """
    print("======== Waiting for response ========")
    #Since the API does not work for requests for page sizes larger than 2000,
    # set this threshold to prevent unexpected user error
    if int(limit) > 2000:
        print('The maximum page size for the CMR API is 2000. Setting the page size limit to 2000.')
        limit = 2000
    metaUrl = granuleMetaUrl
    #example: kwargs.items() = [[concept_id, 'C504319-GHRC']]
    #basically this appends the search parameters passed in by the user
    # to the main url.
    for k, v in kwargs.items():
        metaUrl += "&{}={}".format(k, v)
    #loop through the pages. Note here we take (total-1/limit). int() chops
    # off the decimal (i.e. takes the value to the floor), thus we add 2.
    # if we did total+1/limit, we would add 1.
    # format the url with each page number based on this calculation
    metaResult = []
    metaResult.extend([requests.get(metaUrl.format(limit,pagenum)).text
                  for pagenum in range(1, int((total - 1) / limit) + 2)])
    # The first can be the error msgs
    root = ElementTree.XML(metaResult[0])
    if root.tag == "errors":
        print(" |- Error: " + str([ch.text for ch in root._children]))
        return

    metaResult = [ref for res in metaResult
                  for ref in XmlListConfig(ElementTree.XML(res))[2:]]
    locationResult = _searchResult(granuleUrl, total=total, limit=limit, **kwargs)
    #zip everything into a dictionary list and return to the main program.
    return [Granule(m, l) for m, l in zip(metaResult, locationResult)]

def searchCollection(total=1, limit=1, **kwargs):
    """
    Search the CMR collections
    :param total: the number of results desired
    :param limit: limit of the size of the page (2000 max)
    :param kwargs: search parameters
    :return: list of results (<Instance of Result>)
    """
    print("======== Waiting for response ========")
    #Since the API does not work for requests for page sizes larger than 2000,
    # set this threshold to prevent unexpected user error
    if int(limit) > 2000:
        print('The maximum page size for the CMR API is 2000. Setting the page size limit to 2000.')
        limit = 2000
    metaUrl = collectionMetaUrl
    #example: kwargs.items() = [[concept_id, 'C504319-GHRC']]
    #basically this appends the search parameters passed in by the user
    # to the main url.
    for k, v in kwargs.items():
        metaUrl += "&{}={}".format(k, v)

    #loop through the pages. Note here we take (total-1/limit). int() chops
    # off the decimal (i.e. takes the value to the floor), thus we add 2.
    # if we did total+1/limit, we would add 1.
    # format the url with each page number based on this calculation
    metaResult = []
    metaResult.extend([requests.get(metaUrl.format(limit,pagenum)).json()
                  for pagenum in range(1, int((total - 1) / limit) + 2)])
    #Try to get the json entry from each of the entries in the api response
    try:
        metaResult = [ref for res in metaResult
                  for ref in res['feed']['entry']]
    except KeyError:
        print (" |- Error: " + str((json.loads(metaResult[0].text))["errors"]))
        return
    locationResult = _searchResult(collectionUrl, total=total, limit=limit, **kwargs)
    #zip everything into a dictionary list and return to the main program.
    return [Collection(m, l) for m, l in zip(metaResult, locationResult)]
