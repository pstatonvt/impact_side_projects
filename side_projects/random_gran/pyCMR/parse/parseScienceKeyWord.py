import csv
import urllib.request
import ssl
import requests

class parseScienceKeyWord():

    def __init__(self):
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/sciencekeywords/sciencekeywords.csv"
        #response = urllib.request.urlopen(ResourcesTypeURL, context=gcontext)
        #f = csv.reader(response)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.Topic = []
        self.Term = []
        self.Category = []
        self.Variable_Level_1 = []
        self.Variable_Level_2 = []
        self.Variable_Level_3 = []
        self.Detailed_Variable = []
        self.UUID = []

        next(f)  # Skip the first two line information
        next(f)
        for item in f:
            self.Category.append(item[0:1])
            self.Topic.append(item[1:2])
            self.Term.append(item[2:3])
            self.Variable_Level_1.append(item[3:4])
            self.Variable_Level_2.append(item[4:5])
            self.Variable_Level_3.append(item[5:6])
            self.Detailed_Variable.append(item[6:7])
            self.UUID.append(item[7:8])

        '''
        for i in range(7):
            SciKeyWords[i] = list(set(SciKeyWords[i]))
        return SciKeyWords

        for res in f:
            if(line_num > 1):
                self.Category.append(res[0].strip(" \""))
                self.Topic.append(res[1].strip(" \""))
                self.Term.append(res[2].strip(" \""))
                self.Variable_Level_1.append(res[3].strip(" \""))
                self.Variable_Level_2.append(res[4].strip(" \""))
                self.Variable_Level_3.append(res[5].strip(" \""))
                self.Detailed_Variable.append(res[6].strip(" \""))
                self.UUID.append(res[7][1:-2])
            line_num += 1
        '''
    def getColumn(self,val):
        if (val == "" or val == None):
            return None
        if(val in self.Category):
            return 'Category'
        if(val in self.Topic):
            return 'Topic'
        if(val in self.Term):
            return 'Term'
        if(val in self.Variable_Level_1):
            return 'Variable_Level_1'
        if (val in self.Variable_Level_2):
            return 'Variable_Level_2'
        if (val in self.Variable_Level_3):
            return 'Variable_Level_3'
        if (val in self.Detailed_Variable):
            return 'Detailed_Variable'
        if (val in self.UUID):
            return 'UUID'
        return None
    def getVariable_Level_1(self,val):
        if(val in self.Variable_Level_1):
            return True
        return False
    def getVariable_Level_2(self,val):
        if(val in self.Variable_Level_2):
            return True
        return False
    def getVariable_Level_3(self,val):
        if(val in self.Variable_Level_3):
            return True
        return False
    def getTerm(self,val):
        if(val in self.Term):
            return True
        return False
    def getTopic(self,val):
        if(val in self.Topic):
            return True
        return False
    def getCategory(self,val):
        if(val in self.Category):
            return True
        return False

if __name__ == "__main__":
    x = parseScienceKeyWord()
    print(x.getColumn("EARTH SCIENCE"))
