import csv
import urllib.request
import ssl
import requests

class parseHori():

    def __init__(self):
        ResourcesTypeURL = "https://gcmdservices.gsfc.nasa.gov/static/kms/horizontalresolutionrange/horizontalresolutionrange.csv?ed_wiki_keywords_page"
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = requests.get(ResourcesTypeURL).text.split('\n')
        f = csv.reader(response, delimiter=',')

        self.Horizontal_Resolution_Range = []
        self.UUID = []

        next(f)
        next(f)
        for item in f:
            self.Horizontal_Resolution_Range.append(item[0:1])
            self.UUID.append(item[1:2])


        '''
        line_num = 0
        for res in data:
            if(line_num > 1):
                self.Horizontal_Resolution_Range.append(res[0].strip(" \""))
                self.UUID.append(res[1].strip(" \"\n"))
            line_num += 1
        '''

    def getColumn(self,val):
        if(val == "" or val == None):
            return None
        if(val in self.Horizontal_Resolution_Range):
            return 'Horizontal_Resolution_Range'
        if(val in self.UUID):
            return 'UUID'
        return None

    def getHorizontal_Resolution_Range(self,val):
        if(val in self.Horizontal_Resolution_Range):
            return True
        return False

if __name__ == "__main__":
    x = parseHori()
    print(x.getColumn("NOT APPLICABLE"))
