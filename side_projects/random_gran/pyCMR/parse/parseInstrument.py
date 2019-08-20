import csv
import urllib.request
import ssl
import requests

class parseInstrument():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/instruments/instruments.csv"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.Class_ = []
        self.Type = []
        self.Category = []
        self.Subtype = []
        self.shortName = []
        self.longName = []
        self.UUID = []

        next(f)
        next(f)

        for item in f:
            self.Class_.append(item[0:1])
            self.Type.append(item[1:2])
            self.Category.append(item[2:3])
            self.Subtype.append(item[3:4])
            self.shortName.append(item[4:5])
            self.longName.append(item[5:6])
            self.UUID.append(item[6:7])

        '''
        for res in data:
            if(line_num > 1):
                self.Category.append(res[0].strip(" \""))
                self.Class_.append(res[1].strip(" \""))
                self.Type.append(res[2].strip(" \""))
                self.Subtype.append(res[3].strip(" \""))
                self.shortName.append(res[4].strip(" \""))
                self.longName.append(res[5].strip(" \""))
                self.UUID.append(res[6].strip(" \"\n"))
            line_num += 1
        '''
    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Category):
            return 'Category'
        if(val in self.Class_):
            return 'Class'
        if (val in self.Type):
            return 'Type'
        if (val in self.Subtype):
            return 'Subtype'
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

if __name__ == "__main__":
    x = parseInstrument()
    print(x.getColumn("NOT APPLICABLE"))
