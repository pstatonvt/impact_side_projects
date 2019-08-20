import csv
import urllib.request
import ssl
import requests

class parseProjects():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/projects/projects.csv"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.Bucket = []
        self.shortName = []
        self.longName = []
        self.UUID = []

        next(f)
        next(f)
        for item in f:
            self.Bucket.append(item[0:1])
            self.shortName.append(item[1:2])
            self.longName.append(item[2:3])
            self.UUID.append(item[3:4])

        '''
        line_num = 0
        for res in data:
            if(line_num > 1):
                self.Bucket.append(res[0].strip(" \""))
                self.shortName.append(res[1].strip(" \""))
                self.longName.append(res[2].strip(" \""))
                self.UUID.append(res[3].strip(" \"\n"))
            line_num += 1
        '''

    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Bucket):
            return 'Bucket'
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
    x = parseProjects()
    print(x.getColumn("AAWS"))
