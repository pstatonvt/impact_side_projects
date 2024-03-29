import csv
import urllib.request
import ssl
import requests

class parseRuncontenttype():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/rucontenttype/rucontenttype.csv"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')
        self.Type = []
        self.Subtype = []
        self.UUID = []

        next(f)
        next(f)
        for item in f:
            self.Type.append(item[0:1])
            self.Subtype.append(item[1:2])
            self.UUID.append(item[2:3])


        '''
        line_num = 0
        for line in data:
            if(line_num > 1):
                self.Type.append(line[0].strip(" \""))
                self.Subtype.append(line[1].strip(" \""))
                self.UUID.append(line[2].strip(" \"\n"))
            line_num += 1
        '''


    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Type):
            return 'Type'
        if(val in self.Subtype):
            return 'Subtype'
        if(val in self.UUID):
            return 'UUID'
        return None
    def getType(self,val):
        if(val in self.Type):
            return True
        return False
    def getSubType(self,val):
        if(val in self.Subtype):
            return True
        return False

if __name__ == "__main__":
    x = parseRuncontenttype()
    print(x.getColumn("GET DATA"))
