import csv
import urllib.request
import ssl
import requests

class parsePlatform():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/platforms/platforms.csv"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.entity = []
        self.shortName = []
        self.Category = []
        self.longName = []
        self.UUID = []

        next(f)
        next(f)
        for item in f:
            self.entity.append(item[0:1])
            self.shortName.append(item[1:2])
            self.Category.append(item[2:3])
            self.longName.append(item[3:4])
            self.UUID.append(item[4:5])

        '''
        line_num = 0
        for res in data:
            if(line_num > 1):
                self.Category.append(res[0].strip(" \""))
                self.entity.append(res[1].strip(" \""))
                self.shortName.append(res[2].strip(" \""))
                self.longName.append(res[3].strip(" \""))
                self.UUID.append(res[4].strip(" \"\n"))
            line_num += 1
        '''

    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Category):
            return 'Category'
        if(val in self.entity):
            return 'Series_Entity'
        if(val in self.shortName):
            return 'Short_Name'
        if(val in self.longName):
            return 'Long_Name'
        if (val in self.UUID):
            return 'UUID'
        return None
    def getShortName(self,val):
        if(val in self.shortName):
            return True
        return False
    def getLongName(self,val):
        if(val in self.longName):
            return True
        return False
    def getCategory(self,val):
        if(val in self.Category):
            return True
        return False
if __name__ == "__main__":
    x = parsePlatform()
    print(x.getColumn("Douglas DC-6"))
