#import the libraries required for the script
import urllib
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import numpy as np

class utilities():

    def __init__(self):
        self.daac_map = {'ASF':['ASF'],'ASDC':['LARC','LARC_ASDC'], 'CDDIS':['CDDIS'],
                    'GES_DISC':['GES_DISC'], 'GHRC':['GHRC','LANCEAMSR2'],
                    'LAADS':['LAADS','LANCEMODIS'], 'LPDAAC':['LPDAAC_ECS'],
                    'NSIDC':['NSIDCV0','NSIDC_ECS'],'OBDAAC':['OB_DAAC'],
                    'ORNL':['ORNL_DAAC'],'PODAAC':['PODAAC'],'SEDAC':['SEDAC']}

    ###############################################################################################
    ############################### Begin Function Collection IDs #################################
    ###############################################################################################
    #This is a function Collection_IDs that requires and 1 input variable (should be the daac name).
    #input: daac - DAAC name
    #output: 1) CID - list of concept IDs ; 2) location - list of CMR urls ; 3) entry_title - list of short names
    #Example: cids, locs, names = Collection_IDs('GHRC')
    def Collection_IDs(self,daac,project):
        #create a mapping for daacs and provider ids in CMR
        #daac_map = {'ASF':['ASF'],'ASDC':['LARC','LARC_ASDC'], 'CDDIS':['CDDIS'],
        #            'GES_DISC':['GES_DISC'], 'GHRC':['GHRC','LANCEAMSR2'],
        #            'LAADS':['LAADS','LANCEMODIS'], 'LPDAAC':['LPDAAC_ECS'],
        #            'NSIDC':['NSIDCV0','NSIDC_ECS'],'OBDAAC':['OB_DAAC'],
        #            'ORNL':['ORNL_DAAC'],'PODAAC':['PODAAC'],'SEDAC':['SEDAC']}
        #
        #Now we need to loop through each of the provider ids assigned to each daac respectively
        #initialize empty arrays to append the record information
        CID = []
        location = []
        entry_title = []
        for pid in self.daac_map[daac]:
            #Query the API to get the complete list of collections for the DAAC provided.
            # Note: since ASF has restricted access records, we do not get the full list
            # unless we have restricted access permissions. Thus, do not query the API for
            # ASF.
            if pid is not 'ASF':
                #set the page size to 2000 so that all the records are returned in a single query.
                # Note: This may change in the future as the code becomes more robust
                ps = 2000
                #replace spaces in the project name with %20 to make it compatible with url
                #proj = project.replace(" ","%20")
                #Query the API based on the DAAC and the page size provided
                #url = 'https://cmr.earthdata.nasa.gov/search/collections?provider_id=' + pid + '&project=' + proj + '&page_size=' + "{:d}".format(ps)
                url = 'https://cmr.earthdata.nasa.gov/search/collections?provider_id=' + pid + '&page_size=' + "{:d}".format(ps)
                # retrieve the xml from the API using the urllib library
                api = urllib.request.urlopen(url)
                #parse the xml file using the xml library
                e = ET.parse(api)
            # if ASF, parse the xml file saved locally
            else:
                e = ET.parse('ASF_holdings.xml')

            #retrieve the structure of the xml file
            tree = ET.ElementTree(e)
            root = tree.getroot()
            #find all of the concept ids, entry titles, and cmr locations of each collection in the XML
            CIDS = root.findall('.//id')
            NAMES = root.findall('.//name')
            LOCS = root.findall('.//location')
            #Use the python script to identify records reviewed in Phase I.
            #reviewed = get_reviewed(daac) # commenting out the reviewed list for future application
            #for each of the tags identified as 'id' iterate to see if the
            # concept ID was reviewed in Phase I. If so, do not append that
            # collection to the concept_id, location, and entry_title arrays
            for i,elem in enumerate(CIDS):
                #note: elem.text is the text contained between the tag <id>Concept_ID</id>
                #if elem.text not in reviewed: # commenting out the check for not reviewed for future application
                CID.append(elem.text)
                #note: LOCS[i].text is the text contained between the tag <location>URL/revision_id</location>
                location.append(LOCS[i].text)
                #note: NAMES[i].text is the text contained between the tag <name>short name</name>
                entry_title.append(NAMES[i].text)

            #return these arrays to the main function
        return CID, location, entry_title

    ###############################################################################################
    ################################ End Function Collection IDs ##################################
    ###############################################################################################

    ###############################################################################################
    ################################ Begin Function Provider IDs ##################################
    ###############################################################################################
    def get_pids(self):
        #base path to the cmr api
        base = 'https://cmr.earthdata.nasa.gov/search/'
        #search the api to pull the collection level metadata
        url = base + 'collections?tag_key=gov.nasa.eosdis'
        api = urllib.request.urlopen(url)
        #parse the xml file using the xml library
        e = ET.parse(api)
        tree = ET.ElementTree(e)
        root = tree.getroot()
        #get the number of hits from using the tag identifier "hits"
        #note: the extension.text stores the value of the hits tag as a string
        # value and int converts it to an integer
        gct = int(root.find('.//hits').text)
        #change the page_size to 2000 to establish one large query of the api
        page_size = "2000"

        #the api is limited to a page_size of 2000. Given the page size above,
        # this line of code takes the number of granules, divides it by the page_size,
        # and rounds up to get the number of pages necessary to scrape all of the
        # granules.
        pages = int(np.ceil(gct/int(page_size)))
        #initialize the data center list
        dc_list = []

        #loop through each page and save the data centers into a list
        for i in range(1,pages+1):
            #set up the url to get the collection level data center information
            url = base + 'collections.json?tag_key=gov.nasa.eosdis&page_size=' + page_size + '&page_num=' + "{:d}".format(i)
            #use the requests library to get the api output
            api = requests.get(url=url)
            #loop through each of the collections to get the data center
            for ent in api.json()['feed']['entry']:
                #if the data center is not already in the list, add it
                if ent['data_center'] not in dc_list:
                    dc_list.append(ent['data_center'])

        return dc_list
    ###############################################################################################
    ################################# End Function Provider IDs ###################################
    ###############################################################################################

    ###############################################################################################
    ################################## Begin Function Projects ####################################
    ###############################################################################################
    def get_projects(self,daac):
        pids = self.daac_map[daac]
        #base path to the cmr api
        base = 'https://cmr.earthdata.nasa.gov/search/'
        #change the page_size to 2000 to establish one large query of the api
        page_size = "1"
        #initialize the data center list
        project_list = []

        #loop through each page and save the data centers into a list
        for pid in pids:
            #set up the url to get the collection level data center information
            url = base + 'collections.json?tag_key=gov.nasa.eosdis&provider_id=' + pid + '&page_size=1&page_num=1&include_facets=true'
            #use the requests library to get the api output
            api = requests.get(url=url)
            #loop through each of the collections to get the data center
            fields = api.json()['feed']['facets']
            #find the location of the project field in the facets dictionary and extract the values-counts
            projects = next(item for item in fields if item.get("field") == "project").get('value-counts')
            #take the project name from each list and append it to our existing project_list list
            project_list.extend([item[0] for item in projects])
        return project_list
    ###############################################################################################
    ################################### End Function Projects #####################################
    ###############################################################################################

    ###############################################################################################
    ############################ Begin Function Iso Topic Categories ##############################
    ###############################################################################################
    def iso_topic_category(self):

        url = 'https://gcmd.nasa.gov/add/serfguide/iso_topic_category.html'
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
        iso_list = []

        for table in soup.find_all('table'):
           for line in table.find_all('li'):
               if not line.text.startswith('The'):
                   iso_list.append(line.text)

        return iso_list
    ###############################################################################################
    ############################# End Function Iso Topic Categories ###############################
    ###############################################################################################

    ###############################################################################################
    ############################### Begin Function Product Titles #################################
    ###############################################################################################
    def get_titles(self,daac):
        keywords = {'ASF':['ASF+DAAC'],'ASDC':['ASDC+DAAC'], 'CDDIS':['CDDIS'],
                    'GES_DISC':['GES+DISC'], 'GHRC':['GHRC+DAAC','LANCE+AMSR2'],
                    'LAADS':['LAADS','LANCE+MODIS'], 'LPDAAC':'LPDAAC',
                    'NSIDC':['NSIDC+DAAC'],'OBDAAC':['OB.DAAC'],
                    'ORNL':['ORNL+distributed+archive+center'],'PODAAC':['PO.DAAC'],
                    'SEDAC':['NASA+Socioeconomic+Data+and+Applications+Center+%28SEDAC%29']}

        if daac != 'ORNL' and daac != 'SEDAC':
            dois = []
            titles = []
            for keyword in keywords[daac]:
                url = 'https://wiki.earthdata.nasa.gov/display/DOIsforEOSDIS/' + keyword
                html = requests.get(url=url)
                soup = BeautifulSoup(html.text, 'lxml')
                souparr = soup.find_all('tr')
                for sp in souparr[1:]:
                    tr = sp.find_all('td')
                    if 'NULL' not in tr[2]:
                        dois.append(tr[0].text)
                        titles.append(tr[1].text)
        else:
            for keyword in keywords[daac]:
                url = 'https://ezid.cdlib.org/search/results?filtered=t&c_title=t&c_identifier=t&publisher=&object_type=&creator=&title=&pubyear_from=&keywords=' + keyword + '&filtered=t&identifier=&pubyear_to=&id_type=&submit_checks=Apply+Changes'
                html = requests.get(url=url)
                soup = BeautifulSoup(html.text, 'lxml')
                test = soup.find('title').text.split()[6]
                spl = test.split(',')
                count = ''
                flag = False
                for i in range(0,len(spl)):
                    count += spl[i]

                url += '&p=1&ps=' + count

                html = requests.get(url)
                soup = BeautifulSoup(html.text, 'lxml')
                dois = []
                titles = []
                table = soup.find('table',{'class':'table3'})
                for tr in table.find_all('tr')[1:]:
                    td = tr.find_all('td')
                    dois.append(td[1].text)
                    titles.append(td[0].text)

        return dict(zip(dois,titles))
    ###############################################################################################
    ################################ End Function Product Titles ##################################
    ###############################################################################################

    ###############################################################################################
    ################################ Begin Function Bounding Box ##################################
    ###############################################################################################
    def get_bounds(cid):
        #base path to the cmr api
        base = 'https://cmr.earthdata.nasa.gov/search/'
        #search the api to pull the collection level metadata
        url = base + 'collections.json?concept_id=' + cid
        #use the requests library to get the api output
        api = requests.get(url=url)
        #set up a fail safe to check if the collection level metadata defines a bounding box
        # or point geometry information
        try:
            #convert the output to json and parse the bounding box coordinates
            coords = api.json()['feed']['entry'][0]['boxes'][0].split()
            typ = 'box'
            #the coordinates are provided as a 4-element list in order of south, west, north, east
            south = float(coords[0])
            west  = float(coords[1])
            north = float(coords[2])
            east  = float(coords[3])

            #use the api to get the number of granules for the collection
            #note: page_size 1 limits the length of the api retrn
            page_size = "1"
            #create the url to obtain the granule information from the api
            url = base + 'granules?concept_id=' + cid + '&page_size=' + page_size
            #use the requests library to get the api output
            api = urllib.request.urlopen(url)
            #parse the xml file using the xml library
            e = ET.parse(api)
            tree = ET.ElementTree(e)
            root = tree.getroot()
            #get the number of hits from the using the tag identifier "hits"
            #note: the extension.text stores the value of the hits tag as a string
            # value and int converts it to an integer
            gct = int(root.find('.//hits').text)
            #change the page_size to 2000 to establish one large query of the api
            page_size = "2000"
            #initialize the granule level bounding box information
            gsouth = 9999
            gwest = 9999
            gnorth = -9999
            geast = -9999
            #the api is limited to a page_size of 2000. Given the page size above,
            # this line of code takes the number of granules, divides it by the page_size,
            # and rounds up to get the number of pages necessary to scrape all of the
            # granules.
            pages = int(np.ceil(gct/int(page_size)))
            #loop through each page
            for i in range(1,pages+1):
                #set up the url to get the granule level geometry information
                url = base + 'granules.json?concept_id=' + cid + '&page_size=' + page_size + '&page_num=' + "{:d}".format(i)
                url = base + 'granules.json?concept_id=' + cid + '&page_size=' + page_size + '&page_num=' + "{:d}".format(i)
                #use the requests library to get the api output
                api = requests.get(url=url)
                #loop through each of the granules to get the coordinate information
                for ent in api.json()['feed']['entry']:
                    #try to get the coordinates using the boxes key
                    try:
                        coords = ent['boxes'][0].split()
                        gsouth = min(gsouth,float(coords[0]))
                        gwest = min(gwest,float(coords[1]))
                        gnorth = max(gnorth,float(coords[2]))
                        geast = max(geast,float(coords[3]))
                    #if that doesn't work, keep moving through the script
                    except:
                        pass
                    #try to get the coordinates from the polygons key
                    try:
                        coords = ent['polygons'][0][0].split()
                        coords = [float(coord) for coord in coords]
                        gsouth = min(gsouth,min(coords[::2]))
                        gwest = min(gwest,min(coords[1::2]))
                        gnorth = max(gnorth,max(coords[::2]))
                        geast = max(geast,max(coords[1::2]))
                    #if that doesn't work, keep moving through the script
                    except:
                        pass
                    #try to get the coordinates from the points key
                    try:
                        coords = ent['points'][0].split()
                        gsouth = min(gsouth,coords[0])
                        gwest = min(gwest,coords[1])
                        gnorth = max(gnorth,coords[0])
                        geast = max(geast,coords[1])
                    #try to get the coordinates from the lines key
                    #if that doesn't work, keep moving through the script
                    except:
                        pass
                    try:
                        coords = ent['lines'][0].split()
                        gsouth = min(gsouth,coords[::2])
                        gwest = min(gwest,coords[1::2])
                        gnorth = max(gnorth,coords[::2])
                        geast = max(geast,coords[1::2])
                    #if that doesn't work, keep moving through the script
                    except:
                        pass


            ###########################################################################
            ### May need to include buffers here depending on conversation with CMR ###
            ###########################################################################
            #https://wiki.earthdata.nasa.gov/display/CMR/CMR+Data+Partner+User+Guide#CMRDataPartnerUserGuide-Tolerance
            #set up a valid flag if the granule level value is outside of the collection level value
            # the flag is set to false. If it is within the collection level value, the flag is set
            # to true
            if gsouth < south:  #can potentially implement a threshold of 0.0001 here
                sflag = "The collection level and granule level metadata disagree. Recommend changing the spatial extent of the collection level to fully include the extent of the granules:\nCollection Latitude: " + "{:f}".format(south).rstrip('0').rstrip('.') + "\nGranule Latitude: " + "{:f}".format(gsouth).rstrip('0').rstrip('.')
            else:
                sflag = "OK"

            #set up a valid flag if the granule level value is outside of the collection level value
            # the flag is set to false. If it is within the collection level value, the flag is set
            # to true
            if gwest < west:    #can potentially implement a threshold of 0.0001 here
                wflag = "The collection level and granule level metadata disagree. Recommend changing the spatial extent of the collection level to fully include the extent of the granules:\nCollection Longitude: " + "{:f}".format(west).rstrip('0').rstrip('.') + "\nGranule Longitude: " + "{:f}".format(gwest).rstrip('0').rstrip('.')
            else:
                wflag = "OK"
           #set up a valid flag if the granule level value is outside of the collection level value
            # the flag is set to false. If it is within the collection level value, the flag is set
            # to true
            if gnorth > north:  #can potentially implement a threshold of 0.0001 here
                nflag = "The collection level and granule level metadata disagree. Recommend changing the spatial extent of the collection level to fully include the extent of the granules:\nCollection Latitude: " + "{:f}".format(north).rstrip('0').rstrip('.') + "\nGranule Latitude: " + "{:f}".format(gnorth).rstrip('0').rstrip('.')
            else:
                nflag = "OK"

            #set up a valid flag if the granule level value is outside of the collection level value
            # the flag is set to false. If it is within the collection level value, the flag is set
            # to true
            if geast > east:    #can potentially implement a threshold of 0.0001 here
                eflag = "The collection level and granule level metadata disagree. Recommend changing the spatial extent of the collection level to fully include the extent of the granules:\nCollection Longitude: " + "{:f}".format(east).rstrip('0').rstrip('.') + "\nGranule Longitude: " + "{:f}".format(geast).rstrip('0').rstrip('.')
            else:
                eflag = "OK"

            ###########################################################################
            #set up lists for the collection level, granule level, and flag values
            coll = [south,west,north,east]
            gran = [gsouth,gwest,gnorth,geast]
            flag = [sflag,wflag,nflag,eflag]

        #if that doesn't work, continue
        except:
            #if the collection level geometry data is given as a point, the code skips to here
            try:
                #convert the output to json and points coordinates
                coords = api.json()['feed']['entry'][0]['points'][0].split()
                typ = 'point'
                #the coordinates are provided as a 2-element list in order of lat,lon
                lat = float(coords[0])
                lon = float(coords[1])

                #use the api to get the number of granules for the collection
                #note: page_size 1 limits the length of the api retrn
                page_size = "1"
                #create the url to obtain the granule information from the api
                url = base + 'granules?concept_id=' + cid + '&page_size=' + page_size
                #use the requests library to get the api output
                api = urllib.request.urlopen(url)
                #parse the xml file using the xml library
                e = ET.parse(api)
                tree = ET.ElementTree(e)
                root = tree.getroot()
                #get the number of hits from the using the tag identifier "hits"
                #note: the extension.text stores the value of the hits tag as a string
                # value and int converts it to an integer
                gct = int(root.find('.//hits').text)
                #change the page_size to 2000 to establish one large query of the api
                page_size = "2000"
                #initialize the granule level point information
                glat = 9999
                glon = 9999

                #the api is limited to a page_size of 2000. Given the page size above,
                # this line of code takes the number of granule, divides it by the page_size,
                # and rounds up to get the number of pages necessary to scrape all of the
                # granules.
                pages = int(np.ceil(gct/int(page_size)))

                #loop through each page
                for i in range(1,pages+1):
                   #set up the url to get the granule level geometry information
                    url = base + 'granules.json?concept_id=' + cid + '&page_size=' + page_size + '&page_num=' + "{:d}".format(i)
                    #use the requests library to get the api output
                    api = requests.get(url=url)
                    #loop through each of the granules to get the coordinate information
                    for ent in api.json()['feed']['entry']:
                        #try to get the coordinates using the points key
                        try:
                            coords = ent['points'][0].split()
                            coords = [float(coord) for coord in coords]
                            if glat != coords[0]:
                                glat = coords[0]
                            if glon != coords[1]:
                                glon = coords[1]
                        #if that doesn't work, keep moving through the script
                        except:
                            pass
                ###########################################################################
                ### May need to include buffers here depending on conversation with CMR ###
                ###########################################################################
                #https://wiki.earthdata.nasa.gov/display/CMR/CMR+Data+Partner+User+Guide#CMRDataPartnerUserGuide-Tolerance
                #set up a valid flag if the granule level value is not equal to the collection level value
                # the flag is set to false. If it is equal to the collection level value, the flag is set
                # to true
                if glat - lat != 0.: #can potentially implement a threshold of 0.0001 here
                    latflag = "The collection level and granule level metadata disagree. Recommend changing collection level record to match granules:\nCollection Latitude: " + "{:f}".format(lat).rstrip('0').rstrip('.') + "\nGranule Latitude: " + "{:f}".format(glat).rstrip('0').rstrip('.')
                else:
                    latflag = "OK"

                if glon - lon != 0.: #can potentially implement a threshold of 0.0001 here
                    lonflag = "The collection level and granule level metadata disagree. Recommend changing collection level record to match granules:\nCollection Longitude: " + "{:f}".format(lon).rstrip('0').rstrip('.') + "\nGranule Longitude: " + "{:f}".format(glon).rstrip('0').rstrip('.')
                else:
                    lonflag = "OK"

                ###########################################################################
                #set up lists for the collection level, granule level, and flag values
                coll = [lat,lon]
                gran = [glat,glon]
                flag = [latflag,lonflag]
            except:
                pass
        if (typ is not "box") and (len(flag) == 4):
            if flag[0] is not "OK" or flag[2] is not "OK":
                latflag = "The collection level and granule level metadata disagree. Recommend changing collection level record to match granules:\nCollection Latitude: " + "{:f}".format(south).rstrip('0').rstrip('.') + "->" + "{:f}".format(north).rstrip('0').rstrip('.') + "\nGranule Latitude: " + "{:f}".format(gsouth).rstrip('0').rstrip('.') + "->" + "{:f}".format(gnorth).rstrip('0').rstrip('.')
            if flag[1] is not "OK" or flag[3] is not "OK":
                lonflag = "The collection level and granule level metadata disagree. Recommend changing collection level record to match granules:\nCollection Longitude: " + "{:f}".format(west).rstrip('0').rstrip('.') + "->" + "{:f}".format(east).rstrip('0').rstrip('.') + "\nGranule Latitude: " + "{:f}".format(gwest).rstrip('0').rstrip('.') + "->" + "{:f}".format(geast).rstrip('0').rstrip('.')
            flag = [latflag,lonflag]

        #printing the lists for a sanity check
        #for i in range(0,len(coll)):
        #    print("Collection: ", coll[i], "Granule: ", gran[i], "Result: ", flag[i])

        #return the values to the main function
        return flag
    ###############################################################################################
    ################################# End Function Bounding Box ###################################
    ###############################################################################################

#write documentation
class errors():
    def not_provided():
        error_statement = 'np'
        return error_statement
    def okay():
        error_statement = 'OK'
        return error_statement
    def UMM_required(field):
        error_statement = ('**' + field + ' is a required field within the collection-level metadata schema**\n\n')
        return error_statement
    def GCMD_required(field):
        error_statement = ('**' + field + ' is a required field. Recommend adding a ' +
                           'GCMD approved value for ' + field  + '**\n\n')
        return error_statement
    def DIF10_required(field):
        error_statement = ('**' + field + ' is a required field within the DIF10 collection-level metadata schema**')
        return error_statement
    def UMM_recommended(field):
        error_statement = ('**Recommend adding a UMM schema approved ' +
                           'value for ' + field + '**\n\n')
        return error_statement
    def GCMD_recommended(field):
        error_statement = ('**Recommend adding a GCMD approved ' +
                           'value for ' + field + '**\n\n')
        return error_statement
    def recommended(field):
        error_statement = ('Recommend adding a value for ' + field)
        return error_statement
    def GCMD(field,val):
        error_statement = ('**This is a GCMD controlled vocabulary field and ' +
                                        val + ' is not included. Recommend changing to ' +
                                        'appropriate GCMD value**\n\n')
        return error_statement
    def UMM(field,val):
        error_statement = ('**This is a UMM schema controlled vocabulary field and ' +
                           val + ' is not included. Recommend changing to ' +
                           'appropriate UMM schema value**\n\n')
        return error_statement
    def EOSDIS(field,val):
        error_statement = ('**This is a EOSDIS controlled vocabulary field and ' +
                           val + ' is not included. Recommend changing to ' +
                           'appropriate EOSDIS value**\n\n')
        return error_statement
    def DATUM():
        error_statement = ('Information about the datum should be provided in the metadata if possible.')
        return error_statement
    def ftp():
        error_statement = ('Recommend either removing the ftp link or replacing the ftp link to https, if applicable')
        return error_statement

    def broken_url():
        error_statement = ('Broken link(s). Please remove from the metadata or provide the correct URL.')
        return error_statement

    def check_link():
        error_statement = (" The error code returned a value of None. Please check this link(s) to confirm it's formatted correctly")
        return error_statement

    def http():
        error_statement = "Recommend updating the link(s) from 'http' to 'https'"
        return error_statement

    def broken_https(url):
        error_statement = "Recommend changing from 'http' to 'https', however, the provided link breaks when converted to 'https.': " + url
        return error_statement

    def date_format_error(date):
        error_statement = "The provided date: " + date + " is not in the correct format (%Y-%m-%dT%H:%M:%SZ)"
        return error_statement

    def date_format_day_error(date):
        error_statement = "The provided date: " + date + " contains a day that is > 31 and < 1. Recommend providing a valid date"
        return error_statement

    def date_format_month_error(date):
        error_statement = "The provided date: " + date + " contains a month that is > 12 and < 1. Recommend providing a valid date"
        return error_statement

    def date_format_future_error(date):
        error_statement = ("The provided date: " +  date + " is in the future. Recommend either:\n" +
                           "a) removing the date from the metadata record and setting the EndsAtPresentFlag to True\n" +
                           "OR b) setting the date in the metadata record to a valid value.")
        return error_statement
    def date_format_inserttime_future_error(date):
        error_statement = ("The provided date: " + date + " is in the future. Recommend providing a valid date for this field")
        return error_statement
