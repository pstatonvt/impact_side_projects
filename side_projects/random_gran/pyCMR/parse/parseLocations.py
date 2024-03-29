import csv
import urllib.request
import ssl
import requests

class parseLocations():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/locations/locations.csv"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.Location_Category = []
        self.Location_Type = []
        self.Location_Subregion1 = []
        self.Location_Subregion2 = []
        self.Location_Subregion3 = []
        self.UUID = []

        next(f)
        next(f)
        for item in f:
            self.Location_Category.append(item[0:1])
            self.Location_Type.append(item[1:2])
            self.Location_Subregion1.append(item[2:3])
            self.Location_Subregion2.append(item[3:4])
            self.Location_Subregion3.append(item[4:5])
            self.UUID.append(item[5:6])

        '''
        line_num = 0
        for res in data:
            if(line_num > 1):
                self.Location_Category.append(res[0].strip(" \""))
                self.Location_Type.append(res[1].strip(" \""))
                self.Location_Subregion1.append(res[2].strip(" \""))
                self.Location_Subregion2.append(res[3].strip(" \""))
                self.Location_Subregion3.append(res[4].strip(" \""))
                self.UUID.append(res[5].strip(" \"\n"))
            line_num += 1
        '''

    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Location_Category):
            return 'Location_Category'
        if(val in self.Location_Type):
            return 'Location_Type'
        if (val in self.Location_Subregion1):
            return 'Location_Subregion1'
        if (val in self.Location_Subregion2):
            return 'Location_Subregion2'
        if(val in self.Location_Subregion3):
            return 'Location_Subregion3'
        if(val in self.UUID):
            return 'UUID'
        return None

    def getLocation_Category(self,val):
        if(val in self.Location_Category):
            return True
        return False

    def getLocation_Type(self,val):
        if(val in self.Location_Type):
            return True
        return False

    def getLocation_Subregion1(self,val):
        if(val in self.Location_Subregion1):
            return True
        return False
    def getLocation_Subregion2(self,val):
        if(val in self.Location_Subregion2):
            return True
        return False
    def getLocation_Subregion3(self,val):
        if(val in self.Location_Subregion3):
            return True
        return False

if __name__ == "__main__":
    x = parseLocations()
    print(x.getColumn("NOT APPLICABLE"))
