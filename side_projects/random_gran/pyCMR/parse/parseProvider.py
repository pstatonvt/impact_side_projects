import csv
import urllib.request
import ssl
import requests

class parseProvider():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/providers/providers.csv"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.Bucket_Level0 = []
        self.Bucket_Level1 = []
        self.Bucket_Level2 = []
        self.Bucket_Level3 = []
        self.Short_Name = []
        self.Long_Name = []
        self.Data_Center_URL = []
        self.UUID = []

        next(f)
        next(f)
        for item in f:
            self.Bucket_Level0.append(item[0:1])
            self.Bucket_Level1.append(item[1:2])
            self.Bucket_Level2.append(item[2:3])
            self.Bucket_Level3.append(item[3:4])
            self.Short_Name.append(item[4:5])
            self.Long_Name.append(item[5:6])
            self.Data_Center_URL.append(item[6:7])
            self.UUID.append(item[7:8])

        '''
        line_num = 0
        for res in data:
            if(line_num > 1):
                self.Bucket_Level0.append(res[0].strip(" \""))
                self.Bucket_Level1.append(res[1].strip(" \""))
                self.Bucket_Level2.append(res[2].strip(" \""))
                self.Bucket_Level3.append(res[3].strip(" \""))
                self.Short_Name.append(res[4].strip(" \""))
                self.Long_Name.append(res[5].strip(" \""))
                self.Data_Center_URL.append(res[6].strip(" \""))
                self.UUID.append(res[7].strip(" \"\n"))
            line_num += 1
        '''
    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Bucket_Level0):
            return 'Bucket_Level0'
        if(val in self.Bucket_Level1):
            return 'Bucket_Level1'
        if (val in self.Bucket_Level2):
            return 'Bucket_Level2'
        if (val in self.Bucket_Level3):
            return 'Bucket_Level3'
        if(val in self.Short_Name):
            return 'Short_Name'
        if(val in self.Long_Name):
            return 'Long_Name'
        if (val in self.Data_Center_URL):
            return 'Data_Center_URL'
        if (val in self.UUID):
            return 'UUID'
        return None
    def getShortName(self,val):
        if(val in self.Short_Name):
            return True
        return False
    def getLongName(self,val):
        if(val in self.Long_Name):
            return True
        return False

if __name__ == "__main__":
    x = parseProvider()
    print(x.getColumn("AALTO"))
