#module for loading data from url using requests

import requests

class Loader():
    timeout_int = 20
    certificateverification_bool = False
    headers_dc = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    protocol_str = 'http'
    urlstrminimumlenght_int = 7#'http://....'
    def __init__(self):
        self.__reset_fc()

    def process_fc(self, url_str, **kwargs_dc):
        '''General function for loading data using arguments
        kwargs_dc - is a dictionary with parameters for url generation: pages, count, locations and etc...
        '''
        self.__reset_fc()
        self.url_str = url_str
        self.kwargs_dc = kwargs_dc
        if self.__isurl_fc():
            if self.kwargs_dc:
                self.kwargs_dc = kwargs_dc
                self.__formaturl_fc()
            print('OK - getting data from url: ', self.url_str)
            self.__getresponse_fc()
        else:
            return self.response_obj

    def process_loadjson_fc(self, url_str, **kwargs_dc):
        '''External funtion for loading url with json data'''
        outputjson_dc = {}
        self.kwargs_dc = kwargs_dc
        self.process_fc(url_str)
        if isinstance(self.response_obj, requests.models.Response):
            try:
                outputjson_dc = self.response_obj.json()
            except Exception as e:
                print(e)
        return outputjson_dc

    def process_loadstring_fc(self, url_str, **kwargs_dc):
        self.kwargs_dc = kwargs_dc
        self.process_fc(url_str)
        if isinstance(self.response_obj, requests.models.Response):
            try:
                return self.response_obj.text
            except Exception as e:
                print(e)
                return ''

    def __getresponse_fc(self):
        '''Getting response using requests'''
        try:
            self.response_obj = requests.get(self.url_str, timeout=self.timeout_int, headers=self.headers_dc, verify=self.certificateverification_bool)
        except Exception as e:
            print(e)

    def __formaturl_fc(self):
        '''Function for formatting url: number of pages'''
        if self.kwargs_dc:
            pass

    def __isurl_fc(self):
        '''Function for validation url format'''
        if isinstance(self.url_str, str):
            if len(self.url_str) > self.urlstrminimumlenght_int:
                if len(self.url_str.split('.'))>1:
                    return True
        return False

    def __reset_fc(self):
        '''Refreshing object'''
        self.url_str = None
        self.response_obj = None
        self.status_int = False
        self.kwargs_dc = dict()

if __name__ == '__main__':
    testurl_str = 'https://shearman.wd1.myworkdayjobs.com/en-US/ShearmanandSterling/0/searchPagination/318c8bb6f553100021d223d9780d30be/0'
    import sys
    loader_obj = Loader()
    output_obj = None
    if len(sys.argv) == 2:
        #python script.py http://somedomain.subdomain/...
        output_obj = loader_obj.process_fc(sys.argv[1])
    elif len(sys.argv) == 3:
        if sys.argv[2] == '-string':
            output_obj = loader_obj.process_loadstring_fc(sys.argv[1])
        elif sys.argv[2] == '-json':
            output_obj = loader_obj.process_loadjson_fc(sys.argv[1])
    else:
        output_obj = loader_obj.process_loadstring_fc(testurl_str)
    print(output_obj)