import csv
import urllib.request
import requests
import socket
import ssl
from datetime import *
from util import errors

PlatformURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/platforms/platforms.csv"
InstrumentURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/instruments/instruments.csv"
ProjectURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/projects/projects.csv"
ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/rucontenttype/rucontenttype.csv"

class checkerRules():

    def __init__(self,urls,enums):
        self.urls = urls
        self.storage = []
        self.repeat = []
        self.enums = enums

    def checkGranuleUR(self, val):
        #print("Input of checkGranuleUR() is " + val)
        if val == None:
            return "Provide a granule UR for this granule. This is a required field."
        else:
            return errors.okay()

    def checkInsertTime(self, val):
        #print("Input of checkInsertTime() is " + val)
        try:
            if val == None:
                return errors.not_provided()
            if not val.endswith("Z"):
                return "InsertTime error."
            val = val.replace("Z", "")
            t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond / 1000 > 999:
                return "InsertTime error."
            t_now = datetime.now()
            if t_record.year > t_now.year:
                return "InsertTime error."
            return errors.okay()
        except ValueError:
            return "InsertTime error."

    def checkLastUpdate(self, updateTime, prodTime):
        #print("Input of checkLastUpdate() is " + updateTime + ', ' + prodTime)
        try:
            if updateTime == None:
                return errors.not_provided()
            elif not updateTime.endswith("Z"):
                return "LastUpdate time error."
            updateTime = updateTime.replace("Z", "")
            t_record = datetime.strptime(updateTime, '%Y-%m-%dT%H:%M:%S')
            prodTime = prodTime.replace("Z", "")
            p_record = datetime.strptime(prodTime, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond / 1000 > 999:
                return "LastUpdate time error."
            t_now = datetime.now()
            if t_record.year > t_now.year or t_record < p_record:
                return "LastUpdate time error."
            return errors.okay()
        except ValueError:
            return "LastUpdate time error."

    def checkDeleteTime(self, deleteTime, prodTime):
        #print("Input of checkDeleteTime() is " + deleteTime + ', ' + prodTime)
        try:
            if deleteTime == None:
                return errors.not_provided()
            elif not deleteTime.endswith("Z"):
                return "Delete time error"
            deleteTime = deleteTime.replace("Z", "")
            t_record = datetime.strptime(deleteTime, '%Y-%m-%dT%H:%M:%S')
            prodTime = prodTime.replace("Z", "")
            p_record = datetime.strptime(prodTime, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond / 1000 > 999:
                return "Delete time error"
            if p_record > t_record:
                return "Delete time error"
            return "OK - quality check"
        except ValueError:
            return "Delete time error"

    def checkCollectionShortName(self, sname):
        #print("Input of checkCollectionShortName() is " + sname)
        if sname == None:
            return "np - Ensure the DataSetId field is provided."
        else:
            return errors.okay()

    def checkCollectionVersionID(self, sname):

        #print("Input of checkCollectionVersionID() is " + sname)
        if sname == None:
            return "np - Ensure the DataSetId field is provided."
        else:
            return errors.okay()

    def checkDataSetId(set, val):
        #print("Input of checkDataSetId() is " + val)
        if val == None:
            return "np - Ensure that the ShortName and VersionId fields are provided."
        elif val.isupper() or val.islower():
            return "Recommend that the Dataset Id use mixed case to optimize human readability."
        else:
            return errors.okay()

    def checkSizeMBDataGranule(set, val):
        #print("Input of checkSizeMBDataGranule() is " + val)
        if val == None:
            return "Granule file size not provided. Recommend providing a value for this field in the metadata."
        else:
            return "OK - quality check"

    def checkDayNightFlag(set, val):
        #print("Input of checkDayNightFlag() is " + val)
        DNFlags = ('DAY', 'NIGHT', 'BOTH', 'UNSPECIFIED')
        if val == None:
            return errors.not_provided()
        elif val.upper() not in DNFlags:
            return "Invalid value for DayNightFlag. Valid values include: DAY; NIGHT; BOTH; UNSPECIFIED"
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


    def checkProductionDateTime(self, prodTime, insertTime):
        #print("Input of checkProductionDateTime() is " + prodTime + ', ' + insertTime)
        return self.__checkTimeStr(val, errors.not_provided(),
                                        errors.okay(),
                                        errors_date_format_error(val),
                                        errors_date_format_day_error(val),
                                        errors_date_format_month_error(val),
                                        errors_date_format_inserttime_future_error(val))
        '''
        try:
            if prodTime == None:
                return errors.not_provided()
            if not prodTime.endswith("Z"):
                return "ProductionDateTime error"
            prodTime = prodTime.replace("Z", "")
            p_record = datetime.strptime(prodTime, '%Y-%m-%dT%H:%M:%S')
            insertTime = insertTime.replace("Z", "")
            i_record = datetime.strptime(insertTime, '%Y-%m-%dT%H:%M:%S')
            if p_record.microsecond / 1000 > 999:
                return "ProductionDateTime error"
            t_now = datetime.now()
            if p_record > t_now:
                return "ProductionDateTime error"
            elif p_record != i_record:
                return "Format OK - does not match the InsertTime"
            return errors.okay()
        except ValueError:
            return "ProductionDateTime error"
        '''
    def checkTemporalSingleTime(self, val):
        #print("Input of checkTemporalSingleTime() is " + val)
        return self.__checkTimeStr(val, errors.not_provided(),
                                        errors.okay(),
                                        errors_date_format_error(val),
                                        errors_date_format_day_error(val),
                                        errors_date_format_month_error(val),
                                        errors_date_format_inserttime_future_error(val))
        '''
        try:
            if val == None:
                return errors.not_provided()
            if not val.endswith("Z"):
                return "SingleDateTime error"
            val = val.replace("Z", "")
            t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond / 1000 > 999:
                return "SingleDateTime error"
            t_now = datetime.now()
            if t_record.year > t_now.year:
                return "SingleDateTime error"
            return "OK - quality check"
        except ValueError:
            return "SingleDateTime error"
        '''
    def checkTemporalBeginningTime(self, val):
        #print("Input of checkTemporalBeginningTime() is " + val)
        return self.__checkTimeStr(val,
                                   "Please provide a beginning date time for this dataset.",
                                   "OK - quality check",
                                   errors.date_format_error(val),
                                   errors.date_format_day_error(val),
                                   errors.date_format_month_error(val),
                                   errors.date_format_future_error(val))
        '''
        try:
            if val == None:
                return errors.not_provided()
            if not val.endswith("Z"):
                return "BeginningDateTime error"
            val = val.replace("Z", "")
            t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond / 1000 > 999:
                return "BeginningDateTime error"
            t_now = datetime.now()
            if t_record.year > t_now.year:
                return "BeginningDateTime error"
            return "OK - quality check"
        except ValueError:
            return "BeginningDateTime error"
        '''

    def checkTemporalEndingTime(self, val):
        #print("Input of checkTemporalEndingTime() is " + val)
        return self.__checkTimeStr(val,
                                   "Please provide a beginning date time for this dataset.",
                                   "OK - quality check",
                                   errors.date_format_error(val),
                                   errors.date_format_day_error(val),
                                   errors.date_format_month_error(val),
                                   errors.date_format_future_error(val))
        '''
        try:
            if val == None:
                return errors.not_provided()
            if not val.endswith("Z"):
                return "EndingDateTime error"
            val = val.replace("Z", "")
            t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
            if t_record.microsecond / 1000 > 999:
                return "EndingDateTime error"
            t_now = datetime.now()
            if t_record.year > t_now.year:
                return "EndingDateTime error"
            return "OK - quality check"
        except ValueError:
            return "EndingDateTime error"
        '''
    def checkBoundingRectangle(self, val):
        #print("Input of checkBoundingRectangle() is ...")

        if val['WestBoundingCoordinate'] == None or val['NorthBoundingCoordinate'] == None or val[
            'EastBoundingCoordinate'] == None or val['SouthBoundingCoordinate'] == None:
            return "Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., " + \
                   "Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., " + \
                   "Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., " + \
                   "Check for other spatial identifiers (Point; GPolygon; or Line). A spatial extent identifier is required., "

        msg = ''
        if float(val['WestBoundingCoordinate']) >= -180 and float(val['WestBoundingCoordinate']) <= 180:
            if float(val['EastBoundingCoordinate']) > float(val['WestBoundingCoordinate']):
                msg += val['WestBoundingCoordinate']+" OK - quality check, "
            else:
                msg += "The East and West Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "
        if float(val['NorthBoundingCoordinate']) >= -90 and float(val['NorthBoundingCoordinate']) <= 90:
            if float(val['SouthBoundingCoordinate']) < float(val['NorthBoundingCoordinate']):
                msg += val['NorthBoundingCoordinate']+" OK - quality check, "
            else:
                msg += "The North and South Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "
        if float(val['EastBoundingCoordinate']) >= -180 and float(val['EastBoundingCoordinate']) <= 180:
            if float(val['EastBoundingCoordinate']) > float(val['WestBoundingCoordinate']):
                msg += val['EastBoundingCoordinate']+" OK - quality check, "
            else:
                msg += "The East and West Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "
        if float(val['SouthBoundingCoordinate']) >= -90 and float(val['SouthBoundingCoordinate']) <= 90:
            if float(val['SouthBoundingCoordinate']) < float(val['NorthBoundingCoordinate']):
                msg += val['SouthBoundingCoordinate']+" OK - quality check, "
            else:
                msg += "The North and South Bounding Coordinates may have been switched., "
        else:
            msg += "The coordinate does not fall within a valid range., "
        return msg

        # Added Co-Ordinates to OK - quality check such as "18.00 OK - quality check"
        # Update request by Jeanne and Updated by Siva - 02/20/2018

    def checkEquatorCrossingTime(self, val, length):
        #print("Input of checkEquatorCrossingTime() is ...")
        if length == 1:
            return self.__checkTimeStr(val, errors.not_provided(),
                                            errors.okay(),
                                            errors_date_format_error(val),
                                            errors_date_format_day_error(val),
                                            errors_date_format_month_error(val),
                                            errors_date_format_inserttime_future_error(val))
            '''
            try:
                if val == None:
                    return errors.not_provided()
                if not val.endswith("Z"):
                    return "DateTime error"
                val = val.replace("Z", "")
                t_record = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
                if t_record.microsecond / 1000 > 999:
                    return "DateTime error"
                t_now = datetime.now()
                if t_record.year > t_now.year:
                    return "DateTime error"
                return "OK - quality check"
            except ValueError:
                return "DateTime error"
            '''
        else:
            for i in range(0, length):
                return self.__checkTimeStr(val['EquatorCrossingDateTime'], errors.not_provided(),
                                                errors.okay(),
                                                errors_date_format_error(val),
                                                errors_date_format_day_error(val),
                                                errors_date_format_month_error(val),
                                                errors_date_format_inserttime_future_error(val))
                '''
                try:
                    if val['EquatorCrossingDateTime'] == None:
                        return errors.not_provided()
                    if not val['EquatorCrossingDateTime'].endswith("Z"):
                        return "DateTime error"
                    val['EquatorCrossingDateTime'] = val['EquatorCrossingDateTime'].replace("Z", "")
                    t_record = datetime.strptime(val['EquatorCrossingDateTime'], '%Y-%m-%dT%H:%M:%S')
                    if t_record.microsecond > 999:
                        return "DateTime error"
                    t_now = datetime.now()
                    if t_record.year > t_now.year:
                        return "DateTime error"
                    return "OK - quality check"
                except ValueError:
                    return "DateTime error"
                '''

    def checkPlatformShortName(self, val, length):
        #print("Input of checkPlatformShortName() is ...")
        PlatformKeys = list()
        PlatformLongNames = list()
        response = requests.get(PlatformURL).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            PlatformKeys += item[2:3]
            PlatformLongNames += item[3:4]
        PlatformKeys = list(set(PlatformKeys))
        PlatformLongNames = list(set(PlatformLongNames))

        if length == 1:
            if val == None:
                return errors.not_provided()
            if val not in PlatformKeys:
                if val in PlatformLongNames:
                    return val + ": incorrect keyword order"
                else:
                    return "The keyword does not conform to GCMD"
        else:
            for i in range(0, length):
                if val[i]['ShortName'] == None:
                    return errors.not_provided()
                if val[i]['ShortName'] not in PlatformKeys:
                    if val[i]['ShortName'] in PlatformLongNames:
                        return val[i]['ShortName'] + ": incorrect keyword order"
                    else:
                        return "The keyword does not conform to GCMD"
        return "OK - quality check"

    # def checkInstrShortName(self, val, platformNum):
    #     print("Input of checkInstrShortName() is ...")
    #     processInstrCount = 0
    #     InstrumentKeys = list()
    #     InstrumentLongNames = list()
    #     response = urllib.request.urlopen(InstrumentURL)
    #     data = csv.reader(response)
    #     next(data)  # Skip the first two line information
    #     next(data)
    #     for item in data:
    #         if len(item) != 0:
    #             InstrumentKeys += item[4:5]
    #             InstrumentLongNames += item[5:6]
    #     InstrumentKeys = list(set(InstrumentKeys))
    #     InstrumentLongNames = list(set(InstrumentLongNames))
    #     response.close()

    #     if platformNum == 1:
    #         try:
    #             if val['Instruments']['Instrument']['ShortName'] == None:
    #                 return errors.not_provided()
    #             if not any(s.lower() == val['Instruments']['Instrument']['ShortName'].lower() for s in InstrumentKeys):
    #                 if val['Instruments']['Instrument']['ShortName'] in InstrumentLongNames:
    #                     return val['Instruments']['Instrument'][instr]['ShortName'] + ": incorrect keyword order"
    #                 else:
    #                     return "The keyword does not conform to GCMD"
    #             processInstrCount += 1
    #         except TypeError:
    #             instrNum = len(val['Instruments']['Instrument'])
    #             for instr in range(0, instrNum):
    #                 if val['Instruments']['Instrument'][instr]['ShortName'] == None:
    #                     return errors.not_provided()
    #                 if not any(s.lower() == val['Instruments']['Instrument'][instr]['ShortName'].lower() for s in InstrumentKeys):
    #                     if val['Instruments']['Instrument'][instr]['ShortName'] in InstrumentLongNames:
    #                         return val['Instruments']['Instrument'][instr]['ShortName'] + ": incorrect keyword order"
    #                     else:
    #                         return "The keyword does not conform to GCMD"
    #                 processInstrCount += 1
    #         except KeyError:
    #             print("Access Key Error!")
    #     else:
    #         for i in range(0, platformNum):
    #             try:
    #                 if val[i]['Instruments']['Instrument']['ShortName'] == None:
    #                     return errors.not_provided()
    #                 if not any(s.lower() == val[i]['Instruments']['Instrument']['ShortName'].lower() for s in InstrumentKeys):
    #                     if val[i]['Instruments']['Instrument']['ShortName'] in InstrumentLongNames:
    #                         return val[i]['Instruments']['Instrument']['ShortName'] + ": incorrect keyword order"
    #                     else:
    #                         return "The keyword does not conform to GCMD"
    #                 processInstrCount += 1
    #             except TypeError:
    #                 instrNum = len(val[i]['Instruments']['Instrument'])
    #                 for instr in range(0, instrNum):
    #                     if val[i]['Instruments']['Instrument'][instr]['ShortName'] == None:
    #                         return errors.not_provided()
    #                     if not any(s.lower() == val[i]['Instruments']['Instrument'][instr]['ShortName'].lower() for s in InstrumentKeys):
    #                         if val[i]['Instruments']['Instrument'][instr]['ShortName'] in InstrumentLongNames:
    #                             return val[i]['Instruments']['Instrument'][instr]['ShortName'] + ": incorrect keyword order"
    #                         else:
    #                             return "The keyword does not conform to GCMD"
    #                     processInstrCount += 1
    #             except KeyError:
    #                 continue
    #     if processInstrCount != 0:
    #         return "OK - quality check"
    #     else:
    #         return errors.not_provided()

    def checkInstrShortName(self, val, platformNum, instruments):
        #print("Input of checkInstrShortName() is ...")
        processInstrCount = 0
        InstrumentKeys = instruments[4]
        SensorResult = ''

        if platformNum == 1:
            val = [val]
            '''
            try:
                # -------
                try:
                    val['Instruments']['Instrument']['Sensors']['Sensor']
                    if val['Instruments']['Instrument']['Sensors']['Sensor']['ShortName'] == \
                            val['Instruments']['Instrument']['ShortName']:
                        SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                except TypeError:
                    sensor_len = len(val['Instruments']['Instrument']['Sensors'])
                    for s in range(sensor_len):
                        try:
                            if val['Instruments']['Instrument']['Sensors'][s]['Sensor']['ShortName'] == \
                                    val['Instruments']['Instrument']['ShortName']:
                                SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                                break
                        except KeyError:
                            continue
                except KeyError:
                    SensorResult = 'np'
                # if len(SensorResult) == 0:
                #     SensorResult = 'Recommend removing sensors from the metadata; since this field will be deprecated in the future.'
                # -------
                if val['Instruments']['Instrument']['ShortName'] == None:
                    return errors.not_provided(), SensorResult
                if not any(s.lower() == val['Instruments']['Instrument']['ShortName'].lower() for s in InstrumentKeys):
                    return "The keyword does not conform to GCMD.", SensorResult
                processInstrCount += 1
            except TypeError:
                instrNum = len(val['Instruments']['Instrument'])
                for instr in range(0, instrNum):
                    # -------
                    try:
                        val['Instruments']['Instrument'][instr]['Sensors']['Sensor']
                        if val['Instruments']['Instrument'][instr]['Sensors']['Sensor']['ShortName'] == \
                                val['Instruments']['Instrument'][instr]['ShortName']:
                            SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                    except TypeError:
                        sensor_len = len(val['Instruments']['Instrument'][instr]['Sensors'])
                        for s in range(sensor_len):
                            try:
                                if val['Instruments']['Instrument'][instr]['Sensors'][s]['Sensor']['ShortName'] == \
                                        val['Instruments']['Instrument'][instr]['ShortName']:
                                    SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                                    break
                            except KeyError:
                                continue
                    except KeyError:
                        SensorResult = errors.not_provided()
                    # if len(SensorResult) == 0:
                    #     SensorResult = 'Recommend removing sensors from the metadata; since this field will be deprecated in the future.'
                    # -------
                    if val['Instruments']['Instrument'][instr]['ShortName'] == None:
                        return errors.not_provided(), SensorResult
                    if not any(s.lower() == val['Instruments']['Instrument'][instr]['ShortName'].lower() for s in
                               InstrumentKeys):
                        return "The keyword does not conform to GCMD.", SensorResult
                    processInstrCount += 1
            except KeyError:
                print("Access Key Error!")
            '''
        #else:
        for i in range(0, platformNum):
            try:
                # -------
                try:
                    val[i]['Instruments']['Instrument']['Sensors']['Sensor']
                    if val[i]['Instruments']['Instrument']['Sensors']['Sensor']['ShortName'] == \
                            val[i]['Instruments']['Instrument']['ShortName']:
                        SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                except TypeError:
                    sensor_len = len(val[i]['Instruments']['Instrument']['Sensors'])
                    for s in range(sensor_len):
                        try:
                            if val[i]['Instruments']['Instrument']['Sensors'][s]['Sensor']['ShortName'] == \
                                    val[i]['Instruments']['Instrument']['ShortName']:
                                SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                                break
                        except KeyError:
                            SensorResult = errors.not_provided()
                            continue
                except KeyError:
                    SensorResult = errors.not_provided()
                # if len(SensorResult) == 0:
                #     SensorResult = 'Recommend removing sensors from the metadata; since this field will be deprecated in the future.'
                # -------
                if val[i]['Instruments']['Instrument']['ShortName'] == None:
                    return errors.not_provided(), SensorResult
                if not any(s.lower() == val[i]['Instruments']['Instrument']['ShortName'].lower() for s in
                           InstrumentKeys):
                    return "The keyword does not conform to GCMD.", SensorResult
                processInstrCount += 1
            except TypeError:
                instrNum = len(val[i]['Instruments'])
                for instr in range(0, instrNum):
                    # -------
                    try:
                        val[i]['Instruments']['Instrument'][instr]['Sensors']['Sensor']
                        if val[i]['Instruments']['Instrument'][instr]['Sensors']['Sensor']['ShortName'] == \
                                val[i]['Instruments']['Instrument'][instr]['ShortName']:
                            SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                    except TypeError as e:
                        try:
                            sensor_len = len(val[i]['Instruments']['Instrument'][instr]['Sensors'])
                            for s in range(sensor_len):
                                try:
                                    if val[i]['Instruments']['Instrument'][instr]['Sensors'][s]['Sensor'][
                                        'ShortName'] == val[i]['Instruments']['Instrument'][instr]['ShortName']:
                                        SensorResult = "Same as Instrument/ShortName. Consider removing since this is redundant information."
                                        break
                                except KeyError:
                                    continue
                        except TypeError:
                            return "Provide at least one relevant instrument for this dataset. This is a required field.", errors.not_provided()
                    except KeyError:
                        SensorResult = errors.not_provided()
                    # if len(SensorResult) == 0:
                    #     SensorResult = 'Recommend removing sensors from the metadata; since this field will be deprecated in the future.'
                    # -------
                    if val[i]['Instruments']['Instrument'][instr]['ShortName'] == None:
                        return errors.not_provided(), SensorResult
                    if not any(s.lower() == val[i]['Instruments']['Instrument'][instr]['ShortName'].lower() for s in
                               InstrumentKeys):
                        return "The keyword does not conform to GCMD.", SensorResult
                    processInstrCount += 1
            except KeyError:
                continue
        if processInstrCount != 0:
            return "OK- quality check", SensorResult
        else:
            return errors.not_provided(), SensorResult

    # def checkSensorShortName(self, val, platformNum):
    #     print("Input of checkInstrShortName() is ...")
    #     processInstrCount = 0
    #     SensorShortNames = list()
    #     SensorLongNames = list()
    #     response = urllib.request.urlopen(InstrumentURL)
    #     data = csv.reader(response)
    #     next(data)  # Skip the first two line information
    #     next(data)
    #     for item in data:
    #         if len(item) != 0:
    #             SensorShortNames += item[4:5]
    #             SensorLongNames += item[5:6]
    #     SensorShortNames = list(set(SensorShortNames))
    #     SensorLongNames = list(set(SensorLongNames))
    #     response.close()


    def checkCampaignShortName(self, val, campaignNum):
        #print("Input of checkCampaignShortName() is ...")
        CampaignKeys = list()
        CampaignLongNames = list()
        response = requests.get(ProjectURL).text.split('\n')        
        data = csv.reader(response)
        next(data)  # Skip the first two line information
        next(data)
        for item in data:
            if len(item) != 0:
                CampaignKeys += item[1:2]
                CampaignLongNames += item[2:3]
        CampaignKeys = list(set(CampaignKeys))
        CampaignLongNames = list(set(CampaignLongNames))

        if campaignNum == 1:
            if val == None:
                return errors.not_provided()
            elif val not in CampaignKeys:
                if val in CampaignLongNames:
                    return val + ": incorrect keyword order"
                else:
                    return "The keyword does not conform to GCMD."
            else:
                return errors.okay()
        else:
            for i in range(campaignNum):
                if val[i]['Campaign']['ShortName'] == None:
                    return errors.not_provided()
                elif val[i]['Campaign']['ShortName'] not in CampaignKeys:
                    if val[i]['Campaign']['ShortName'] in CampaignLongNames:
                        return val[i]['Campaign']['ShortName'] + ": incorrect keyword order"
                    else:
                        return "The keyword does not conform to GCMD."
                else:
                    return errors.okay()

    def checkURL(self, url):
        msg = False
        try:
            request = urllib.request.urlopen(url)
            if request.code == 200:
                if request.code == 200 and not url.startswith('https://'):
                    try:
                        tmp = url.split('//')
                        request = requests.get("https://" + tmp[-1])
                        msg = errors.http()
                    except:
                        msg = errors.okay()
            elif request.code < 400 and request.code >= 300:
                msg = errors.check_link()
            elif request.code >= 400:
                msg = errors.broken_url()
            else:
                msg = errors.check_link()
        except urllib.request.HTTPError as e:
            msg = errors.broken_url()
        except urllib.request.URLError as e:
            msg = errors.check_link()

        if not msg and not url.startswith('ftp'):
            msg = errors.okay()
        elif url.startswith('ftp'):
            msg = errors.ftp()
        else:
            pass
        return msg

    def checkOnlineAccessURL(self, val, length):
        #print("Input of checkOnlineAccessURL() is ...")
        check = [] ; broken = [] ; okay = [] ; ftp = [] ; http = []
        if length == 1:
            if val == None:
                return errors.not_provided()
            error = self.checkURL(val) + '\n' + val[i]['URL']
            return error
        else:
            error = ''
            for i in range(0, length):
                if val[i]['URL'] == None:
                    return errors.not_provided()
                else:
                    if self.checkURL(val[i]['URL']) == errors.check_link():
                        check.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.broken_url():
                        broken.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.http():
                        http.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.ftp():
                        ftp.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.okay():
                        okay.append(val[i]['URL'])

            if len(check) > 0:
               error += errors.check_link() + '\n' + '\n'.join(check)
            if len(broken) > 0:
               error += errors.broken_url() + '\n' + '\n'.join(check)
            if len(http) > 0:
               error += errors.http() + '\n' + '\n'.join(check)
            if len(ftp) > 0:
               error += errors.ftp() + '\n' + '\n'.join(check)
            if len(okay) > 0 and (len(check) == 0 or len(broken) == 0 or len(http) == 0 or len(ftp) == 0):
               error += errors.okay()

            return error

    def checkOnlineAccessURLDesc(self, val, length):
        #print("Input of checkOnlineAccessURLDesc() is ...")

        if length == 1:
            if val == None:
                return "Recommend providing a description for each Online Access URL."
        else:
            for i in range(0, length):
                if val[i]['URLDescription'] == None:
                    return "Recommend providing a description for each Online Access URL."
        return "OK - quality check"

        # Added code for MimeType Checking
        # Update request by Jeanne - Updated by Siva  - 02/20/2018

    def checkOnlineAccessURLMimeType(self, val, length):
        #print("Input of checkOnlineAccessURLMimeType() is ...")
        listItem = self.enums['URLMimeTypeEnum']
        if length == 1:
            if val == None:
                return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
            elif val not in listItem:
                return "Invalid mime type"
            else:
                return "OK - quality check"
        else:
            for i in range(0, length):
                try:
                    if val[i]["MimeType"] == None:
                        return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
                    if (val[i]["MimeType"].lower() not in listItem):
                        return "Invalid mime type"
                    else:
                        return "OK - quality check"
                except:
                    return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"

    def checkOnlineResourceURL(self, val, length):
        #print("Input of checkOnlineResourceURL() is ...")
        #print("Input of checkOnlineAccessURL() is ...")
        check = [] ; broken = [] ; okay = [] ; ftp = [] ; http = []
        if length == 1:
            if val == None:
                return errors.not_provided()
            error = self.checkURL(val) + '\n' + val[i]['URL']
            return error
        else:
            error = ''
            for i in range(0, length):
                if val[i]['URL'] == None:
                    return errors.not_provided()
                else:
                    if self.checkURL(val[i]['URL']) == errors.check_link():
                        check.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.broken_url():
                        broken.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.http():
                        http.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.ftp():
                        ftp.append(val[i]['URL'])
                    elif self.checkURL(val[i]['URL']) == errors.okay():
                        okay.append(val[i]['URL'])

            if len(check) > 0:
               error += errors.check_link() + '\n' + '\n'.join(check)
            if len(broken) > 0:
               error += errors.broken_url() + '\n' + '\n'.join(check)
            if len(http) > 0:
               error += errors.http() + '\n' + '\n'.join(check)
            if len(ftp) > 0:
               error += errors.ftp() + '\n' + '\n'.join(check)
            if len(okay) > 0 and (len(check) == 0 or len(broken) == 0 or len(http) == 0 or len(ftp) == 0):
               error += errors.okay()
        return error

    def checkOnlineResourceDesc(self, val, length):
        #print("Input of checkOnlineResourceDesc() is ...")
        if length == 1:
            if val == None:
                return errors.not_provided()
            else:
                return "OK - quality check"
        else:
            flag = False
            flag1 = False
            flag2 = False
            descs = []
            for i in range(0, length):
                try:
                    if val[i]["Description"] != None:
                        flag = True
                        if val[i]["Description"] not in descs:
                            descs.append(val[i]["Description"])
                        else:
                            flag1 = True
                    else:
                        flag2 = True
                except KeyError:
                    flag2 = True
            if (flag and flag2):
                return "Recommend providing a description for each Online Access URL."
            elif (flag1):
                return "Descriptions should be unique to each URL. Several of the descriptions are repeated in this record. Recommend changing descriptions to more accurately and uniquely describe the URL."
            elif (flag and not flag1 and not flag2):
                return "OK - quality check"
            else:
                return errors.not_provided()

    #Added code for MimeType Checking
    #Update request by Jeanne - Updated by Siva  - 02/20/2018

    def checkOnlineResourceMimeType(self, val, length):
        #print("Input of checkOnlineResourceMimeType() is ...")
        listItem = self.enums['URLMimeTypeEnum']
        if length == 1:
            if val == None:
                return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
            else:
                return "OK - quality check"
        else:
            for i in range(0, length):
                try:
                    if val[i]["MimeType"] != None:
                        return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"
                    if (val[i]["MimeType"].lower() not in listItem):
                        return "Invalid mime type"
                    else:
                        return "OK - quality check"
                except:
                    return "np - reminder: a mime type should be provided for all SERVICE links (Service URL Types in UMM-Common: Access Map Viewer/ Access Mobile App/ Access Web Service/ DIF/ Map Service/ NOMADS/ Opendap Data/ OpenSearch/ SERF/ Software Package/ SSW/ Subsetter/ THREDDS Data)"

    def checkOnlineResourceType(self, val, length):
        #print("Input of checkOnlineResourceType() is ...")
        ResourcesTypes = list()
        response = requests.get(ResourcesTypeURL).text.split('\n')
        data = csv.reader(response)
        next(data)  # Skip the first two row information
        next(data)
        for item in data:
            ResourcesTypes += item[0:1]
        ResourcesTypes = list(set(ResourcesTypes))
        UmmEnumTypes = self.enums['RelatedUrlTypeEnum']
        UmmEnumTypes.extend(self.enums['RelatedURLSubTypeEnum'])
        listA = ["THREDDS CATALOG", "THREDDS DATA", "THREDDS DIRECTORY", "GET WEB MAP FOR TIME SERIES",
                 "GET RELATED VISUALIZATION", "GIOVANNI", "WORLDVIEW", "GET MAP SERVICE"]
        listB = ["GET WEB MAP SERVICE (WMS)", "GET WEB COVERAGE SERVICE (WCS)", "OPENDAP DATA (DODS)"]
        Results = [[],[],[],[],[]]

        if length == 1:
            val = [val]
        for v in val:
            try:
                t = v['Type']
                if t in listA:
                    Results[1].append(t)
                elif t in listB:
                    Results[2].append(t)
                elif t in UmmEnumTypes:
                    Results[3].append(t)
                else:
                    Results[4].append(t)
            except Exception as e:
                return "Each Online Resource URL must be accompanied by a URL Type. Valid values can be found in the UMM-Common schema. A type may be selected from either the URL Type enum or the URL Subtype enum. https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/v1.10/umm-cmn-json-schema.json"
        if Results[4]:
            return "Invalid URL Types: " + "; ".join(Results[4]) + "\nA valid type may be selected from either the URL Type enum or the URL Subtype enum. https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/v1.10/umm-cmn-json-schema.json"
        # result = "; ".join(['; '.join(r) for r in Results[1:3] if r])
        elif Results[2]:
            return "OK - two points for data accessability score for providing an advanced service for visualization, subsetting or aggregation which also meets common framework requirements for standard API based data access."
        elif Results[1]:
            return "OK - one point for data accessability score for providing an advanced service for visualization, subsetting or aggregation"
        elif Results[0]:
            return errors.okay()
        else:
            return errors.not_provided()


    def checkOrderable(self, val):
        #print("Input of checkOrderable() is " + val)
        if val == None:
            return errors.not_provided()
        else:
            return "Note: The Orderable field is being deprecated in UMM."

    def checkDataFormat(self, val):
        #print("Input of checkDataFormat() is " + val)
        if val == None:
            return "Recommend providing the data format(s) for this dataset"
        else:
            return "OK " + val

    def checkVisible(self, val):
        print("Input of checkVisible() is " + val)
        if val == None:
            return errors.not_provided()
        else:
            return "Note: The Visible field is being deprecated in UMM."


