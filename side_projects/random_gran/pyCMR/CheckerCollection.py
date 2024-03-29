import csv
import urllib.request
import requests
import socket
from datetime import *
import re
import ssl
from util import errors
class checkerRules():

    def __init__(self,urls,enums):
        self.urls = urls
        self.storage = []
        self.repeat = []
        self.enums = enums

    def checkOnlineResourceDescription(self, val):
        if val not in self.storage:
            self.storage.append(val)
        else:
            self.repeat.append(val)
        if len(self.repeat) == 0:
            return errors.okay()
        else:
            return "Descriptions are being repeated", repeat

    def checkShortName(self, val):
        #print('Input of checkShortName() is ' + val)
        if val == None:
            return 'Provide a short name for this dataset. This is a required field.'
        else:
            return errors.okay()

    def checkVersionID(self, val):
        #print('Input of checkVersionID() is ' + val)
        if val == None:
            return 'Provide a version Id for this dataset. This is a required field.'
        else:
            return errors.okay()

    def __checkTimeStr(self, val, na_msg, ok_msg, f_error,d_error,m_error,fut_error):
        try:
            if val == None:
                return na_msg
            if not val.endswith('Z'):
                return f_error
            if len(val) > 20: # with microsecond
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ')
            if t_record.microsecond / 1000 > 999:
                return f_error
            if t_record.day > 31 or t_record.day <= 0:
                return d_error
            if t_record.month > 12 or t_record.month <= 0:
                return m_error
            t_now = datetime.now()

            if t_record.year > t_now.year:
                return fut_error
            return ok_msg
        except ValueError:
            return f_error



    def checkInsertTime(self, val):
        #print('Input of checkInsertTime() is ' + val)
        return self.__checkTimeStr(val,
                                   'Provide an insert time for this dataset. This is a required field.',
                                   'OK - quality check',
                                   errors.date_format_error(val),
                                   errors.date_format_day_error(val),
                                   errors.date_format_month_error(val),
                                   errors.date_format_inserttime_future_error(val))

    def checkLastUpdate(self, val):
        #print('Input of checkLastUpdate() is ' + val)
        return self.__checkTimeStr(val,
                                   'Provide a last update time for this dataset. This is a required field.',
                                   'OK - quality check',
                                   errors.date_format_error(val),
                                   errors.date_format_day_error(val),
                                   errors.date_format_month_error(val),
                                   errors.date_format_inserttime_future_error(val))

    def checkLongName(self, val):
        #print("Input of checkLongName() is " + val)
        if val == None:
            return errors.not_provided()
        elif val.isupper() or val.islower():
            return "Recommend that the Long Name use mixed case to optimize human readability."
        else:
            return errors.okay()

    def checkCollectionState(self, val):
        ###print("Input of checkCollectionState() is " + val)
        states = self.enums['CollectionProgressEnum']
        if val == None:
            return errors.UMM_required('Collection State') + 'Please Select from the following list: ' + "; ".join(states) + '"'

        elif val not in states:
            return "Invalid value for CollectionState. Please choose a valid CollectionState from the following list: PLANNED; IN WORK; COMPLETE"
        else:
            return errors.okay()

    def checkDateSetID(self, val,shortName):
        #print("Input of checkDateSetID() is " + val)
        if val == None:
            return "Provide a Dataset Id for this dataset. This is a required field."
        elif val.isupper() or val.islower():
            return "Recommend changing the Dataset Id to mixed case to improve human readability."
        #if val == shortName:
        #    return "The DataSetId is identical to the ShortName. DataSetId maps to \"EntryTitle\" in CMR. Since the entry title is supposed to be a descriptive title of the data set; the DataSetId should not be the same as the ShortName."
        else:
            return errors.okay()

    def checkDesc(self, val, title):
        #print("Input of checkDesc() is " + val[0:20])
        msg = ''
        count = 0
        if val == None:
            return "Provide a description for this dataset. This is a required field."
        if len(val) < 75:
            count += 1
            msg += '{:d}'.format(count) + '.'
            msg += 'It is recommended that a more comprehensive description be provided, mimicking a journal abstract that is useful to the science community but also approachable for a first time user of the data.;\n'

        if title not in val:
            count += 1
            msg += '{:d}'.format(count) + '.'
            msg += 'Recommend adding the DOI title in the first sentence of the description.;\n'

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', val)

        for url in urls:
            try:
                connection = urllib.request.urlopen(url)
                if connection:
                    connection.close()
                if not url.startswith('https'):
                    tmp = url.split('//')
                    try:
                        connection = urllib.request.urlopen('https://' + tmp[1])
                        if connection:
                            connection.close()
                            count += 1
                            msg += '{:d}'.format(count) + '.'
                            msg += errors.http(url) + ';\n'
                    except:
                        count += 1
                        msg += '{:d}'.format(count) + '.'
                        msg += errors.broken_https(url) + ';\n'
            except (urllib.request.HTTPError, urllib.request.URLError) as e:
                count += 1
                msg += '{:d}'.format(count) + '.'
                msg += "Broken link: " + url + ";\n"

        entity = re.findall('&[^\s]*',val)

        if len(entity) != 0:
            count += 1
            msg += '{:d}'.format(count) + '.'
            msg += 'The description contains HTML. Please verify the HTML entities are being displayed properly.'

        if(len(msg) == 0):
            msg += "OK - quality check"

        return msg

    def checkDOI(self,val):
        if(val == None):
            return "DOI is a required metadata element for NASA data sets. The DOI element has recently been added to the ECHO10 schema. If the data set has a DOI the DOI string should be provided here. If the data set does not have a DOI then this field should be added once a DOI has been registered for the data set. There may also be certain cases where a data set does not qualify for a DOI."
        return errors.okay()

    def checkDOIAuthority(self, val):
        if val == None:
            return errors.not_provided()
        elif val != "https://doi.org":
            return "The authority should read \"https://doi.org\" for all NASA data sets."
        else:
            return errors.okay()

    def checkCollectionDataType(self,val):
        if(val == None):
            return errors.not_provided()
        return errors.okay()

    def checkOrderable(self, val):
        #print('Input of checkOrderable() is ' + val)
        if val == None:
            return errors.not_provided()
        else:
            return errors.okay()

    def checkVisible(self, val):
        #print('Input of checkVisible() is ' + val)
        if val == None:
            return errors.not_provided()
        else:
            return errors.okay()

    def checkRevisionDate(self, val):
        #print('Input of checkRevisionDate() is ' + val)
        try:
            if val == None:
                return 'Provide a revision date for this dataset. This is a required field.'
            try:
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ')
            if t_record.microsecond / 1000 > 999:
                return 'Revision date error'
            t_now = datetime.now()
            if t_record > t_now:
                return errors.date_format_inserttime_future_error(val)
            if t_record.day > 31 or t_record.day <= 0:
                return errors.date_format_day_error(val)
            if t_record.month > 12 or t_record.month <= 0:
                return errors.date_format_month_error(val)
            return errors.okay()
        except ValueError:
            return errors.date_format_error()
        #Added additional validations for date time day <=31 and month<=12
        #Added by Siva 02/20/2018
    def checkProcCenter(self, val):
        #print('Input of checkProcCenter() is ' + val)
        DateCents = list()
        response = requests.get(self.urls['ArchiveCenterURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first line information
        next(data)
        for item in data:
            DateCents += item[4:5]
        if val == None:
            return errors.not_provided()
        if(val == "GHRC"):
            return "Currently listed as \"GHRC.\" This is a controlled vocabulary field and a value should be chosen from the GCMD \"Data Centers\" keyword list: https://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv. According to GCMD the Processing Center should be listed as \"NASA/MSFC/GHRC\". GCMD should be contacted for a change request if GHRC does not agree with this nomenclature."
        if val in DateCents:
            return errors.okay()
        else:
            return "It is recommended that the ProcessingCenter name be compliant with GCMD vocabulary. Choose a valid ProcessingCenter name from the following list: https://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv. All records from the same DAAC should have the same ProcessingCenter name for consistency."

    def checkProcLevelID(self, val):
        #print('Input of checkProcLevelID() is ' + val)
        levels = self.enums['ProcessingLevelIDEnum']
        if val == None:
            return 'Provide a processing level Id for this dataset. This is a required field.'
        elif val == '1':
            return '\"\'1\' is not a valid Processing Level ID; please choose either \'1A\' or \'1B\'.\"'
        elif val not in levels:
            return 'The ProcessingLevelId is an invalid value. The ProcessingLevelId should be chosen from a list of NASA EOSDIS appoved values which can be found here: https://science.nasa.gov/earth-science/earth-science-data/data-processing-levels-for-eosdis-data-products/'
        else:
            return errors.okay()

    def checkArchiveCenter(self, val):
        #print("Input of checkArchiveCenter() is " + val)
        ArchCents = list()
        response = requests.get(self.urls['ArchiveCenterURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first line information
        next(data)
        for item in data:
            ArchCents += item[4:5]
            # ArchCents += item[5:6]

        # ArchCents = ('ASDC', 'GESDISC', 'LARC', 'SEDAC', 'GHRC', 'NSIDC', 'LPDAAC', 'ORNL_DAAC', 'OB.DAAC', 'Alaska Satellite Facility', 'PO.DAAC', 'CDDIS', 'LAADS')
        if val == None:
            return errors.not_provided()
        if(val == "GHRC"):
            return "Currently listed as \"GHRC.\" This is a controlled vocabulary field and a value should be chosen from the GCMD \"Data Centers\" keyword list: https://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv. According to GCMD the Archive Center should be listed as \"NASA/MSFC/GHRC\". GCMD should be contacted for a change request if GHRC does not agree with this nomenclature."
        if val in ArchCents:
            return errors.okay()
        else:
            return 'It is recommended that the Archive Center name be compliant with GCMD vocabulary. Choose a valid Archive Center name from the following list: http://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv. All records from the same DAAC should have the same archive center name for consistency.'

    def checkExtPub(self, val):
        #print("Input of checkExtPub() is " + val)
        if val == None:
            return errors.not_provided()
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', val)
        if len(urls) == 0:
            return errors.okay()
        for url in urls:
            try:
                connection = urllib.request.urlopen(url)
                if connection:
                    connection.close()
                if not url.startswith('https'):
                    tmp = url.split('//')
                    try:
                        connection = urllib.request.urlopen('https://' + tmp[1])
                        if connection:
                            connection.close()
                            return errors.http(url)
                    except:
                        return errors.broken_https(url)
                else:
                    return errors.okay()
            except (urllib.request.HTTPError, urllib.request.URLError) as e:
                return "Broken link: " + url
        #return "OK - quality check"

    def checkRestrictFlag(self, val):
        #print("Input of checkRestrictFlag() is " + val)
        if val == None:
            return errors.not_provided()
        else:
            return "OK - quality check"

    def checkRestrictionComment(self,val):
        if val == None:
            return errors.not_provided()
        else:
            return "OK - quality check"

    def checkDataFormat(self, val):
        #print("Input of checkDataFormat() is " + val)
        if val == None:
            return "Recommend providing the DataFormat for this data set. If there is more than one DataFormat; each should be listed as a separate element."
        listItems = self.enums['GetDataTypeFormatEnum']
        #listItems = ["hdf", "netcdf", "geotiff", "gml", "geography markup language"]
        if(val.lower() not in [x.lower() for x in listItems]):
            return "OK - DataFormat does not meet framework requirements (i.e. the data is not in one of the following framework approved formats; HDF; NetCDF; GeoTIFF or Geography Markup Language)."
        return "OK " + val.replace(',', ';')

    def checkPrice(self, val):
        #print("Input of checkPrice() is " + val)
        if val == None:
            return errors.not_provided()
        else:
            return errors.okay()

    def checkSpatialKey(self, val):
        '''
        try:
            #print("Input of checkSpatialKey() is " + val)
        except TypeError:
            #print("Input of checkSpatialKey() is ...")
            val = ', '.join(val)
        '''
        if val == None:
            return "Recommend providing a spatial keyword from the following keywords list: https://gcmdservices.gsfc.nasa.gov/static/kms/locations/locations.csv"

        SpatialKeys = list()
        response = requests.get(self.urls['LocationKeywordURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first line information
        for item in data:
            SpatialKeys += item[0:5]    # Skip UUID column
        SpatialKeys = list(set(SpatialKeys))

        newList = []
        for x in SpatialKeys:
            newList.append(x.lower())
        SpatialKeys = newList
        ##print newList

        if ', ' in val:
            for location in val.split(', '):
                if location.lower() not in SpatialKeys:
                    return "The spatial keyword " + location +" is not listed in GCMD or contains an error."
        else:
            if val.lower() not in SpatialKeys:
                return "The spatial keyword " + val +" is not listed in GCMD or contains an error."
        return errors.okay()

    def checkTemporalKeyword(self, val, length):
        #print("Input of checkTemporalKeyword() is ...")
        if length == 1:
            if len(val) != 0:
                return "OK - quality check"
        else:
            for i in range(0, length):
                if len(val[i][Keyword]) != 0:
                    return "OK - quality check"
        return errors.not_provided()

    def checkSingleDateTime(self, val):
        #print("Input of checkSingleDateTime() is " + val)
        try:
            if val == None:
                return errors.not_provided()
            try:
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ')

            val = val.replace("Z", "")
            t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond > 999:
                return "SingleDateTime error"
            t_now = datetime.now()
            if t_record > t_now:
                return errors.date_format_inserttime_future_error(val)
            return "OK - quality check"
        except ValueError:
            return errors.date_format_error(val)

    def checkBeginDateTime(self, val):
        #print("Input of checkBeginDateTime() is " + val)
        return self.__checkTimeStr(val,
                                   "Please provide a beginning date time for this dataset.",
                                   "OK - quality check",
                                   errors.date_format_error(val),
                                   errors.date_format_day_error(val),
                                   errors.date_format_month_error(val),
                                   errors.date_format_future_error(val))

    def checkEndDateTime(self, val):
        #print("Input of checkEndDateTime() is " + val)
        return self.__checkTimeStr(val,
                                   "Please provide an ending date time for this dataset.",
                                   "OK - quality check",
                                   errors.date_format_error(val),
                                   errors.date_format_day_error(val),
                                   errors.date_format_month_error(val),
                                   errors.date_format_future_error(val))

    def checkContactEmail(self, val, length):
        #print("Input of checkContactEmail() is ...")
        if length == 1:
            if val == 'ghrc-dmg@itsc.uah.edu':
                return 'Please change from "ghrc-dmg@itsc.uah.edu" to "support-ghrc@earthdata.nasa.gov" since this is currently listed as the contact email on the GHRC website: https://ghrc.nsstc.nasa.gov/home/contact-us'
        else:
            for i in range(length):
                if val[i]['Email'] == 'ghrc-dmg@itsc.uah.edu':
                    return 'Please change from "ghrc-dmg@itsc.uah.edu" to "support-ghrc@earthdata.nasa.gov" since this is currently listed as the contact email on the GHRC website: https://ghrc.nsstc.nasa.gov/home/contact-us'
        return 'OK - quality check'

    def checkContactPhone(self, val, length):
        #print("Input of checkContactPhone() is ...")
        temp = self.enums['ContactMechanismTypeEnum']
        #try:
        if length == 1:
            val = [val]
        for i in range(0, length):
            for phone in val['Phone']:
                #print("Pringing phones Type : ", phone['Type'])
                if phone['Type'].strip(' \t\r\n') not in temp:
                    return "Choose a phone type from the following list: " + "; ".join(temp)
        return errors.okay()
        #except:
        #    return "Choose a phone type from the following list: Direct Line; Email; Facebook; Fax; Mobile; Modem; Primary; TDD/TTY Phone; Telephone; Twitter; U.S. toll free; Other"
        # Update request by Jeanne - This validation should only apply to Phone/Type - Not for Phone/Number
        # Updated by Siva on 02/20/2018
    def checkContactJobPositionItem(self,val):
        temp = self.enums['DataContactRoleEnum']
        if val.strip(' \t\r\n') in [x.upper() for x in temp]:
            return errors.okay()
        elif val.upper().strip(' \t\r\n') in [x.upper() for x in temp]:
            return "The Job Position must be chosen from a pre-determined list which is case sensitive in CMR. Recommend changing the role from mixed case to all CAPS so that it may pass CMR validation."

        else:
            return '"Choose a contact role from the following list:' + "; ".join(temp) + '"'

    def checkContactJobPosition(self, val):
        #print("Input of checkContactJobPosition() is ...")
        try:
            return self.checkContactJobPositionItem(val['JobPosition']) + ';'
        except:
            result = ''
            length = len(val)
            for i in range(0, length):
                result += self.checkContactJobPositionItem(val[i]['JobPosition']) + ';'
            return result

    def checkContactRole(self, val):
        #print("Input of checkContactRole() is " + val)
        roles = self.enums['DataCenterRoleEnum']
        if val == None:
            return errors.not_provided()
        elif val in roles:
            return errors.okay()
        elif val.upper() not in roles:
            return "This is a controlled vocabulary field. Please choose a contact role from the following list: " "; ".join(roles)
        else:
            return "The Contact Role must be chosen from a pre-determined list which is case sensitive in CMR. Recommend changing the role from mixed case to all CAPS so that it may pass CMR validation."

    def __gcmdHierarchyCheck(self, sciKeyWords, DesiredKeys, ToCheckKey, length, val,
                             does_not_conform_msg, wrong_hierachy_msg, may_remove_msg, ok_msg, np_msg=errors.not_provided()):
        AllKeys = set([k.upper() for level in sciKeyWords for k in level])
        DesiredKeys = set(k.upper() for k in DesiredKeys)
        if not isinstance(val, list):
            val = [val]
        Results = False
        Result2Words = []
        Result3Words = []
        msg = ''
        for i in range(0, length):
            if ToCheckKey not in val[i]:
                return np_msg
            word = val[i][ToCheckKey].upper()
            if word not in DesiredKeys:
                if word is not ' ':
                    Results = True
                elif word not in AllKeys:
                    Result3Words.append(word)
                else:
                    Result2Words.append(word)
        if Results:
            msg += may_remove_msg + '\n'
        if len(Result3Words) != 0:
            msg +=  does_not_conform_msg + " ".join(Result3Words) + '\n'
        if len(Result2Words) != 0:
            msg +=  wrong_hierachy_msg + " ".join(Result2Words) + '\n'
        if msg is '':
            return ok_msg
        else:
            return msg

    def checkSciKeyCategory(self, val, length, sciKeyWords):
        #print("Input of checkSciKeyCategory() is ...")
        DesiredKeys = sciKeyWords[0]
        ToCheckKey = 'CategoryKeyword'
        return self.__gcmdHierarchyCheck(sciKeyWords, DesiredKeys, ToCheckKey, length, val,
                                         "The following science category keywords do not conform to GCMD: ",
                                         "The following science category keywords are in the incorrect position of the science keyword hierarchy: ",
                                         "May Remove",
                                         "OK - quality check")

    def checkSciKeyTopic(self, val, length, sciKeyWords):
        #print("Input of checkSciKeyTopic() is ...")
        DesiredKeys = sciKeyWords[1]
        ToCheckKey = 'TopicKeyword'
        return self.__gcmdHierarchyCheck(sciKeyWords, DesiredKeys, ToCheckKey, length, val,
                                         "The following science category keywords do not conform to GCMD: ",
                                         "The following science category keywords are in the incorrect position of the science keyword hierarchy: ",
                                         "May Remove",
                                         "OK - quality check")

    def checkSciKeyTerm(self, val, length, sciKeyWords):
        #print("Input of checkSciKeyTerm() is ...")
        DesiredKeys = sciKeyWords[2]
        ToCheckKey = 'TermKeyword'
        return self.__gcmdHierarchyCheck(sciKeyWords, DesiredKeys, ToCheckKey, length, val,
                                         "The following science category keywords do not conform to GCMD: ",
                                         "The following science category keywords are in the incorrect position of the science keyword hierarchy: ",
                                         "May Remove",
                                         "OK - quality check")

    def __gcmdLevelCheck(self, sciKeyWords, DesiredKeys, length, val, L1, L2 = None, L3 = None):
        AllKeys = set([k.upper() for level in sciKeyWords for k in level])
        if length == 1:
            val = [val]
        Result2Words = []
        Result3Words = []
        msg = ''
        for i in range(0, length):
            if L3 and L2 and L1:
                if val[i][L1][L2][L3]['Value'] == None:
                    return errors.not_provided()
                word = val[i][L1][L2][L3]['Value']
            elif L2 and L1:
                if val[i][L1][L2]['Value'] == None:
                    return errors.not_provided()
                word = val[i][L1][L2]['Value']
            else:
                if val[i][L1]['Value'] == None:
                    return errors.not_provided()
                word = val[i][L1]['Value']
            word = word.upper()
            if word not in DesiredKeys:
                if word is not ' ':
                    ResultWords = True
                elif word not in AllKeys:
                    Result3Words.append(word)
                else:
                    Result2Words.append(word)
        if ResultWords:
            return "May remove this field from the metadata as the entry is empty"
        if len(Result3Words) != 0:
            return "The following science category keywords do not conform to GCMD: " + " ".join(Result3Words)
        if len(Result2Words) != 0:
            return "The following science category keywords are in the incorrect position of the science keyword hierarchy: " + " ".join(
                Result2Words)
        return "OK - quality check"

    def checkSciKeyVarL1(self, val, length, sciKeyWords):
        #print("Input of checkSciKeyVarL1() is ...")
        return self.__gcmdLevelCheck(sciKeyWords, sciKeyWords[3], length, val,
                                     'VariableLevel1Keyword')

    def checkSciKeyVarL2(self, val, length, sciKeyWords):
        #print("Input of checkSciKeyVarL2() is ...")
        return self.__gcmdLevelCheck(sciKeyWords, sciKeyWords[4], length, val,
                                     'VariableLevel1Keyword',
                                     'VariableLevel2Keyword')

    def checkSciKeyVarL3(self, val, length, sciKeyWords):
        #print("Input of checkSciKeyVarL3() is ...")
        return self.__gcmdLevelCheck(sciKeyWords, sciKeyWords[5], length, val,
                                     'VariableLevel1Keyword',
                                     'VariableLevel2Keyword'
                                     'VariableLevel3Keyword')

    def checkPlatformShortName(self, val, length, platforms):
        #print("Input of checkPlatformShortName() is ...")
        DesiredKeys = platforms[2]
        ToCheckKey = 'ShortName'
        return self.__gcmdHierarchyCheck(platforms, DesiredKeys, ToCheckKey, length, val,
                                         "The following platform short names do not conform to GCMD: ",
                                         "The following platform short names are in the inncorect position of the keyword hierarchy: ",
                                         "May Remove",
                                         "OK - quality check")

    def __checkFieldsNotEqualToRespectively(self, val, length, keyName, targetList, err_msg):
        if length == 1:
            val = [val]
        for i in range(0, length):
            if keyName in val[i] and val[i][keyName].upper() == targetList[i].upper():
                return err_msg
        return None

    def __checkFieldsNotEqualto(self, val, length, keyName, target, err_msg):
        if length == 1:
            val = [val]
        for i in range(0, length):
            if keyName in val[i] and val[i][keyName].upper() == target.upper():
                return err_msg
        return None

    def checkPlatformLongName(self, val, length, ShortNames, platforms):
        #print("Input of checkPlatformLongName() is ...")
        DesiredKeys = platforms[3]
        ToCheckKey = 'LongName'

        ret = self.__checkFieldsNotEqualToRespectively(val, length, ToCheckKey, ShortNames,
                                                       "Same as Platform/ShortName. Either replace with an appropriate Long Name or remove since this is redundant information.")
        if ret:
            return ret
        return self.__gcmdHierarchyCheck(platforms, DesiredKeys, ToCheckKey, length, val,
                                         "The following platform long names do not conform to GCMD: ",
                                         "The following platform long names are in the incorect position of the keyword hierarchy: ",
                                         "May Remove",
                                         "OK - quality check",
                                         np_msg="Recommend adding a Platform long name if applicable.")

    def checkPlatformType(self, val, length, platforms):
        #print("Input of checkPlatformType() is ...")
        DesiredKeys = platforms[0]
        ToCheckKey = 'Type'

        ret = self.__checkFieldsNotEqualto(val, length, ToCheckKey, "IN SITU LAND BASED",
                                           "Change to 'In Situ Land-based Platforms' to conform to GCMD keywords.")
        if ret:
            return ret
        return self.__gcmdHierarchyCheck(platforms, DesiredKeys, ToCheckKey, length, val,
                                         "The following platform type keywords do not conform to GCMD: ",
                                         "The following platform type keywords are in the inncorect position of the keyword hierarchy: ",
                                         "OK- quality check",
                                         np_msg="Add a platform type. Each platform should have an associated type listed in the metadata.")

    def __checkInstrSensor(self, instrumentVals, toCheckKey, dup_msg, check_long_short_dup=False):
        SensorResults = []
        # access instrumentVals as a list
        for instrumentVal in instrumentVals:
            # check sensors
            try:
                sensorVals = instrumentVal['Sensors']['Sensor']
                if not isinstance(sensorVals, list):
                    sensorVals = [sensorVals]

                # I know this is bad. But let's take the badness for just now..
                if check_long_short_dup:
                    ret = self.__checkFieldsNotEqualToRespectivelyByKey(sensorVals, len(sensorVals), "ShortName", "LongName",
                                                                        "Same as Sensor/ShortName. Either replace with an appropriate LongName or remove since this is redundant information.")
                    if ret:
                        SensorResults.append(ret)

                # access sensorVals as a list
                for sensorVal in sensorVals:
                    if sensorVal[toCheckKey] == instrumentVal[toCheckKey]:
                        SensorResults.append(dup_msg)
                        break
            except (KeyError, TypeError): # does not have sensor info
                SensorResults.append(errors.not_provided())
        return "; ".join(SensorResults)

    def checkInstrShortName(self, val, platformNum, instruments):
        #print("Input of checkInstrShortName() is ...")
        processInstrCount = 0
        InstrumentKeys = instruments[4]
        ShortNameResults = []
        SensorResults = []

        if platformNum == 1:
            val = [val]
        for i in range(0, platformNum):
            try:
                # -------
                instrumentVals = val[i]['Instruments']['Instrument']
                if not isinstance(instrumentVals, list):
                    instrumentVals = [instrumentVals]
                # check short names
                ShortNameResults.append(self.__gcmdHierarchyCheck(instruments, InstrumentKeys, "ShortName", len(instrumentVals), instrumentVals,
                                          "The following instrument short names do not conform to GCMD: ",
                                          "The following instrument short names are in the incorrect position of the keyword hierarchy: ",
                                          "May Remove",
                                          "OK - quality check"))

                SensorResults.append(self.__checkInstrSensor(instrumentVals,
                                                             'ShortName',
                                                             "Same as Instrument/ShortName. Consider removing since this is redundant information."))

            except TypeError:
                ShortNameResults.append('An Instrument value is required for each platform. If there is not an instrument for this platform, the value should be "Not Applicable"; ')

            except KeyError: # does not have instrument info
                return "Provide at least one relevant instrument for this dataset. This is a required field.", errors.not_provided()

        return "; ".join(ShortNameResults), "; ".join(SensorResults)


    def __checkFieldsNotEqualToRespectivelyByKey(self, val, length, keyName1, keyName2, err_msg):
        if length == 1:
            val = [val]
        for i in range(0, length):
            if keyName1 in val[i] and keyName2 in val[i] and val[i][keyName1].upper() == val[i][keyName2].upper():
                return err_msg
        return None

    def checkInstrLongName(self, val, platformNum, instruments):
        #print("Input of checkInstrLongName() is ...")
        processInstrCount = 0
        InstrumentKeys = instruments[5]
        LongNameResults = []
        SensorResults = []

        if platformNum == 1:
            val = [val]
        for i in range(0, platformNum):
            try:
                # -------
                instrumentVals = val[i]['Instruments']['Instrument']
                if not isinstance(instrumentVals, list):
                    instrumentVals = [instrumentVals]

                ret = self.__checkFieldsNotEqualToRespectivelyByKey(instrumentVals, len(instrumentVals), "ShortName", "LongName",
                                                              "Same as Instrument/ShortName. Either replace with an appropriate Long Name or remove since this is redundant information.")
                if ret:
                    LongNameResults.append(ret)

                # check long names
                LongNameResults.append(self.__gcmdHierarchyCheck(instruments, InstrumentKeys, "LongName", len(instrumentVals), instrumentVals,
                                                                  "The following instrument long names do not conform to GCMD: ",
                                                                  "The following instrument long names are in the incorrect position of the keyword hierarchy: ",
                                                                  "May Remove",
                                                                  "OK - quality check",
                                                                  np_msg="Recommend providing an Instrument/LongName since many Instrument/ShortNames are comprised of acronyms."))

                SensorResults.append(self.__checkInstrSensor(instrumentVals,
                                                             "LongName",
                                                             "Same as Instrument/LongName. Consider removing since this is redundant information.",
                                                             check_long_short_dup=True))
            except TypeError:
                LongNameResults.append('np ')


            except KeyError: # does not have instrument info
                return "Provide at least one relevant instrument for this dataset. This is a required field.", errors.not_provided()

        return "; ".join(LongNameResults), "; ".join(SensorResults)

    def checkCampaignShortName(self, val, length):
        #print("Input of checkCampaignShortName() is ...")
        CampaignKeys = list()
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(self.urls['ProjectURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            CampaignKeys += item[1:2]
        CampaignKeys = list(set(CampaignKeys))
        if length == 1:
            if val == None:
                return "Provide a campaign name for this dataset. This is a required field."
            if val not in CampaignKeys:
                return "The campaign short name does not conform to GCMD"
        else:
            for i in range(0, length):
                if val[i]['ShortName'] == None:
                    return "Provide a campaign name for this dataset. This is a required field."
                if val[i]['ShortName'] not in CampaignKeys:
                    return "The campaign short name does not conform to GCMD"
        return "OK- quality check"

    def checkCampaignLongName(self, val, length):
        #print("Input of checkCampaignLongName() is ...")
        CampaignKeys = list()
        response = requests.get(self.urls['ProjectURL']).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            CampaignKeys += item[2:3]
        CampaignKeys = list(set(CampaignKeys))
        if length == 1:
            if val == None:
                return "Recommend providing a Campaign/LongName, if applicable."
            if val not in CampaignKeys:
                return "The campaign long name does not conform to GCMD"
        else:
            for i in range(0, length):
                if val[i]['LongName'] == None:
                    return "Recommend providing a Campaign/LongName, if applicable."
                if val[i]['LongName'] not in CampaignKeys:
                    return "The campaign long name does not conform to GCMD"
        return "OK- quality check"

    def checkCampaignStartDate(self, val, length):
        #print("Input of checkCampaignStartDate() is ...")
        try:
            if length == 1:
                if val == None:
                    return errors.not_provided()
                if not val.endswith("Z"):
                    return "Project/StartDate error."
                val = val.replace("Z", "")
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
                if t_record.microsecond > 999:
                    return "Project/StartDate error."
                t_now = datetime.now()
                if t_record > t_now:
                    return "Project/StartDate error."
                return "OK - quality check"
            else:
                for i in range(length):
                    if val[i]['StartDate'] == None:
                        return errors.not_provided()
                    if not val[i]['StartDate'].endswith("Z"):
                        return "Project/StartDate error."
                    val[i]['StartDate'] = val[i]['StartDate'].replace("Z", "")
                    t_record = datetime.strptime(val[i]['StartDate'], '%Y-%m-%dT%H:%M:%S')
                    if t_record.microsecond > 999:
                        return "Project/StartDate error."
                    t_now = datetime.now()
                    if t_record > t_now:
                        return "Project/StartDate error."
                return "OK - quality check"
        except ValueError:
            return "Project/StartDate error."
        except KeyError:
            return errors.not_provided()

    def checkCampaignEndDate(self, val, length):
        #print("Input of checkCampaignEndDate() is ...")
        try:
            if length == 1:
                if val == None:
                    return errors.not_provided()
                if not val.endswith("Z"):
                    return "Project/EndDate error."
                val = val.replace("Z", "")
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
                if t_record.microsecond > 999:
                    return "Project/EndDate error."
                t_now = datetime.now()
                if t_record > t_now:
                    return "Project/EndDate error."
                return "OK - quality check"
            else:
                for i in range(length):
                    if val[i]['EndDate'] == None:
                        return errors.not_provided()
                    if not val[i]['EndDate'].endswith("Z"):
                        return "Project/EndDate error."
                    val[i]['EndDate'] = val[i]['EndDate'].replace("Z", "")
                    t_record = datetime.strptime(val[i]['EndDate'], '%Y-%m-%dT%H:%M:%S')
                    if t_record.microsecond > 999:
                        return "Project/EndDate error."
                    t_now = datetime.now()
                    if t_record > t_now:
                        return "Project/EndDate error."
                return "OK - quality check"
        except ValueError:
            return "Project/EndDate error."
        except KeyError:
            return errors.not_provided()

    def checkOnlineAccessURL(self, val, length, ArchCenter):
        #print("Input of checkOnlineAccessURL() is ...")
        brokenURLcount = 0
        msg = ""
        try:
            url = self.urls['ArchtoURLs'][ArchCenter]
        except KeyError:
            url = ''
        if length == 1:
            if val == None:
                return "No OnlineAccessURL provided. Please provide at least one OnlineAccessURL as this is required in UMM. The OnlineAccessURL should point as directly to the data as possible (i.e. the user should not have to click through sub directories to access data pertinent to this collection) and the link should run through URS."
            if val.startswith('ftp://'):
                return "Please replace the current ftp link with a link to directly download the data via https. The link should run through URS and point as directly to the data as possible (i.e. the user should not have to click through sub directories to access data pertinent to this collection)."
            try:
                connection = urllib.request.urlopen(val)
                if connection:
                    connection.close()
            except (urllib.request.HTTPError, urllib.request.URLError) as e:
                return "Broken link: " + val
        else:
            for i in range(0, length):
                if val[i]['URL'] == None:
                    return "No OnlineAccessURL provided. Please provide at least one OnlineAccessURL as this is required in UMM. The OnlineAccessURL should point as directly to the data as possible (i.e. the user should not have to click through sub directories to access data pertinent to this collection) and the link should run through URS."
                if val[i]['URL'].startswith('ftp://'):
                    return "Please replace the current ftp link with a link to directly download the data via https. The link should run through URS and point as directly to the data as possible (i.e. the user should not have to click through sub directories to access data pertinent to this collection)."
                try:
                    connection = urllib.request.urlopen(val[i]['URL'])
                    if connection:
                        connection.close()
                except (urllib.request.HTTPError, urllib.request.URLError, socket.timeout) as e:
                    msg += "Broken link: " + val[i]['URL'] + ";"
                    brokenURLcount += 1
                    # return "Broken link: " + val[i]['URL']
        if brokenURLcount != 0:
            return msg
        else:
            return errors.okay()

    def checkOnlineURLDesc(self, val, length):
        ##print  val
        msg = ''
        if length == 1:
            if val == None:
                return "Recommend providing a URL description."
        else:
            for i in range(0, length):
                try:
                    if val[i]['URLDescription'] == None:
                        return "Recommend providing descriptions for all Online Access URLs."
                except KeyError:
                    return "Recommend providing descriptions for all Online Access URLs."
        return "OK- quality check"

        # Added code for Mime Type Checking
        # Update request by Jeanne - Updated by Siva 02/20/2018

    def checkOnlineAccessURLMimeType(self, val, length):
        #print("Input of checkOnlineAccessURLMimeType() is ...")
        listItem = self.enums['URLMimeTypeEnum']
        if length == 1:
            if val == None:
                #print("This should be the case")
                return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)" 
            if (val.lower() not in listItem):
                return "Invalid mime type: " + val.lower()
            else:
                return "OK - quality check"
        else:
            for i in range(0, length):
                try:
                    if val[i]["MimeType"] == None:
                        return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
                    if (val[i]["MimeType"].lower() not in listItem):
                        return "Invalid mime type: " + val[i]["MimeType"]
                    else:
                        return "OK - quality check"
                except:
                    return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: " + "; ".join(listItem) + ')"'

    def checkSpatialHorGeoCoor(self, val):
        #print("Input of checkSpatialHorGeoCoor() is " + val)
        if val == None:
            return "np - Please provide a horizontal coordinate system for this dataset. This is a required field."
        else:
            return errors.okay()

    def checkSpatialCorordinateSystem(self,val):
        listItem = self.enums['GranuleSpatialRepresentationEnum']
        if(val == None):
            return 'This field is required in CMR. Provide one of the following values for coordinate system: ' + "; ".join(listItem)

        if(val.upper() in listItem):
            return errors.okay()
        return 'Invalid value for coordinate system. Provide one of the following values for coordinate system: ' + "; ".join(listItem)

    def checkBoundingRectangle(self, val):
        #print("Input of checkBoundingRectangle() is ...")
        msg = ''
        if val['WestBoundingCoordinate'] == None or val['NorthBoundingCoordinate'] == None or val['EastBoundingCoordinate'] == None or val['SouthBoundingCoordinate'] == None:
            return 'Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., ' + \
                   'Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., ' + \
                   'Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., ' + \
                   'Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., '
        if float(val['WestBoundingCoordinate']) >= -180 and float(val['WestBoundingCoordinate']) <= 180:
            if float(val['EastBoundingCoordinate']) > float(val['WestBoundingCoordinate']):
                msg += val['WestBoundingCoordinate']+' OK - quality check; '
            else:
                msg += "The East and West Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "

        if float(val['NorthBoundingCoordinate']) >= -90 and float(val['NorthBoundingCoordinate']) <= 90:
            if float(val['SouthBoundingCoordinate']) < float(val['NorthBoundingCoordinate']):
                msg += val['NorthBoundingCoordinate']+ " OK - quality check; "
            else:
                msg += "The North and South Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "

        if float(val['EastBoundingCoordinate']) >= -180 and float(val['EastBoundingCoordinate']) <= 180:
            if float(val['EastBoundingCoordinate']) > float(val['WestBoundingCoordinate']):
                msg += val['EastBoundingCoordinate']+ " OK - quality check; "
            else:
                msg += "The East and West Bounding Coordinates may have been switched., "
        else:
            msg += "checkOnlineResourceURLThe coordinate does not fall within a valid range., "

        if float(val['SouthBoundingCoordinate']) >= -90 and float(val['SouthBoundingCoordinate']) <= 90:
            if float(val['SouthBoundingCoordinate']) < float(val['NorthBoundingCoordinate']):
                msg += val['SouthBoundingCoordinate']+ " OK - quality check; "
            else:
                msg += "The North and South Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "

        return msg

        #Added Co-Ordinates to OK - quality check such as "18.00 OK - quality check"
        #Update request by Jeanne and Updated by Siva - 02/20/2018

    def checkOnlineResourceURL(self, val, length):
        #print ("Input of checkOnlineResourceURL() is ...")
        brokenURLcount = 0
        msg = ""
        if length == 1:
            if val == None:
                return errors.not_provided()
            try:
                connection = urllib.request.urlopen(val, timeout=5)
                if val.startswith('ftp://'):
                    return "Please replace the current ftp link with a link to directly download the data via https. The link should run through URS and point as directly to the data as possible (i.e. the user should not have to click through sub directories to access data pertinent to this collection)."

                if connection:
                    connection.close()
            except (urllib.request.HTTPError, urllib.request.URLError, socket.timeout) as e:
                return "Broken link: " + val
        else:
            for i in range(0, length):
                try:
                    if val[i]['URL'] == None:
                        return errors.not_provided()
                    if val[i]['URL'].startswith('ftp://'):
                        return "Please replace the current ftp link with a link to directly download the data via https. The link should run through URS and point as directly to the data as possible (i.e. the user should not have to click through sub directories to access data pertinent to this collection)."
                    connection = urllib.request.urlopen(val[i]['URL'], timeout=5)
                    if connection:
                        connection.close()

                except (urllib.request.HTTPError, urllib.request.URLError, socket.timeout) as e:
                    msg += "Broken link: " + val[i]['URL'] + ";"
                    brokenURLcount += 1
                    # return "Broken link: " + val[i]['URL']
        if brokenURLcount != 0:
            return msg
        else:
            return errors.okay()

    def checkOnlineResourceURLDesc(self, val, length):
        #print("Input of checkOnlineResourceURLDesc() is ...")
        msg = ''
        if length == 1:
            if val == None:
                return "Recommend providing a URL description for each Online Resource URL. "
        else:
            for i in range(0, length):
                try:
                    if val[i]['Description'] == None:
                        return "Recommend providing a URL description for each Online Resource URL. "
                except KeyError:
                    return "Recommend providing a URL description for each Online Resource URL. "
        return "OK- quality check"
    #Added code for Mime Type Checking
    #Update request by Jeanne - Updated by Siva 02/20/2018

    def checkOnlineResourceMimeType(self, val, length):
        #print("Input of checkOnlineResourceMimeType() is ...")
        listItem = self.enums['URLMimeTypeEnum']
        if length == 1:
            if val == None:
                error = "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
            else:
                error = "OK - quality check"
        else:
            for i in range(0, length):
                try:
                    if val[i]["MimeType"] == None:
                        error = "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
                    elif (val[i]["MimeType"].lower() not in listItem):
                        error = "Invalid mime type: " + val[i]["MimeType"].lower()
                    else:
                        error = "OK - quality check"
                except:
                    error =  "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"

        return error

    def checkOnlineResourceType(self, val, length):
        #print("Input of checkOnlineResourceType() is ...")

        #UmmEnumTypes = ["GET DATA", "GET SERVICE", "GET RELATED VISUALIZATION", "DATA SET LANDING PAGE", "DOI",
        #       "EXTENDED METADATA", "PROFESSIONAL HOME PAGE", "PROJECT HOME PAGE", "VIEW RELATED INFORMATION",
        #       "HOME PAGE"] + \
        #       ["DATACAST URL", "EARTHDATA SEARCH", "ECHO", "EDG", "EOSDIS DATA POOL", "GDS", "GIOVANNI", "KML",
        #       "LAADS", "LANCE", "LAS", "MIRADOR", "MODAPS", "NOAA CLASS", "ON-LINE ARCHIVE", "REVERB",
        #       "ACCESS MAP VIEWER", "ACCESS MOBILE APP", "ACCESS WEB SERVICE", "DIF", "MAP SERVICE", "NOMADS",
        #       "OPENDAP DATA", "OPENDAP DATA (DODS)", "OPENDAP DIRECTORY (DODS)", "OpenSearch", "SERF", "SOFTWARE PACKAGE",
        #       "SSW", "SUBSETTER", "THREADS CATALOG", "THREADS DATA", "THREDDS DIRECTORY", "WEB COVERAGE SERVICE (WCS)",
        #       "WEB FEATURE SERVICE (WFS)", "WEB MAP FOR TIME SERIES", "WEB MAP SERVICE (WMS)", "WORKFLOW (SERVICE CHAIN)",
        #       "GIBS", "MAP", "ALGORITHM THEORETICAL BASIS DOCUMENT", "CALIBRATION DATA DOCUMENTATION", "DATA QUALITY",
        #       "CASE STUDY", "DATA USAGE", "DELIVERABLES CHECKLIST", "GENERAL DOCUMENTATION", "HOW-TO", "PI DOCUMENTATION",
        #       "PROCESSING HISTORY", "PRODUCTION VERSION HISTORY", "PRODUCT QUALITY ASSESSMENT", "PRODUCT USAGE",
        #       "PRODUCT HISTORY", "PUBLICATIONS", "RADIOMETRIC AND GEOMETRIC CALIBRATION METHODS", "READ-ME",
        #       "RECIPE", "REQUIREMENTS AND DESIGN", "SCIENCE DATA PRODUCT SOFTWARE DOCUMENTATION",
        #       "SCIENCE DATA PRODUCT VALIDATION", "USER FEEDBACK", "USER'S GUIDE"]
        UmmEnumTypes = self.enums['RelatedUrlTypeEnum']
        UmmEnumTypes.extend(self.enums['RelatedURLSubTypeEnum'])
        ListA = ["THREDDS CATALOG", "THREDDS DATA", "THREDDS DIRECTORY", "GET WEB MAP FOR TIME SERIES", "GET RELATED VISUALIZATION", "GIOVANNI", "WORLDVIEW", "GET MAP SERVICE"]
        ListB = ["GET WEB MAP SERVICE (WMS)", "GET WEB COVERAGE SERVICE (WCS)", "OPENDAP DATA (DODS)"]

        Results = [[],[],[],[],[]]

        if length == 1:
            val = [val]
        for v in val:
            try:
                t = v['Type']
                if t in ListA:
                    Results[1].append(t)
                elif t in ListB:
                    Results[2].append(t)
                elif t in UmmEnumTypes:
                    Results[3].append(t)
                else:
                    Results[4].append(t)
            except:
                return "Each Online Resource URL must be accompanied by a URL Type. Valid values can be found in the UMM-Common schema. A type may be selected from either the URL Type enum or the URL Subtype enum. https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/v1.9/umm-cmn-json-schema.json"
        if Results[4]:
            return "Invalid URL Types: " + "; ".join(Results[4])
        # result = "; ".join(['; '.join(r) for r in Results[1:3] if r])
        elif Results[2]:
            return "OK - two points for data accessability score for providing an advanced service for visualization, subsetting or aggregation which also meets common framework requirements for standard API based data access."
        elif Results[1]:
            return "OK - one point for data accessability score for providing an advanced service for visualization, subsetting or aggregation"
        elif Results[0]:
            return errors.okay()
        else:
            return errors.not_provided()

    def checkSpatialGranuleRepresent(self, val):
        #print("Input of checkSpatialGranuleRepresent() is " + val)
        represent_list = self.enums['GranuleSpatialRepresentationEnum']
        if val == None:
            return "Provide a granule spatial representation for this dataset. This is a required field."
        elif val.upper() not in represent_list:
            return "The value for Granule Spatial Representation is invalid. Choose an appropriate replacement from the following list: " + + "; ".join(listItem)
        else:
            return errors.okay()

    def checkSpatInfoHorGeoDatumName(self, val):
        #print("Input of checkSpatInfoHorGeoDatumName() is " + val)
        if val == None:
            return errors.DATUM()
        else:
            return val

    def checkFieldNoneEmpty(self, metadata, path, ok_msg, empty_msg):
        val = metadata
        for hir in path.split('/'):
            try:
                val = val[hir]
                #print("val: ", val)
            except:
                return empty_msg
        if val != None:
            return ok_msg
        else:
            return empty_msg
