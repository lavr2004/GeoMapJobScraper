#module with parser

# ordernumber_startgran_int = 0
# ordernumber_finishgran_int = 0
#
# parserpayloadusualgran_example_dc = {
#     'startgrantitle_str': ('startgranvalue_str', ordernumber_startgran_int),
#     'finishgantitle_str': ('finishgranvalue_str', ordernumber_finishgran_int)
# }
#
# parserpayloadloopexample_dc = {
#     'loop':{#parserpayloadusualgran_example_dc
#         'startgrantitle_str': ('startgranvalue_str', ordernumber_startgran_int),
#         'finishgranvalue_str' : ('finishgranvalue_str', ordernumber_finishgran_int)
#     },
#     'title':parserpayloadusualgran_example_dc,
#     'ref':parserpayloadusualgran_example_dc,
#     'url':parserpayloadusualgran_example_dc
# }

class Cdparser():

    skip_str = '{skip}'

    def _convertgrantolist_fc(self, gran_str):
        '''function for convering gran to reversed list of patterns'''
        if isinstance(gran_str, str):
            return list(reversed(gran_str.split(self.skip_str)))
        return []

    def _searchbyfirstpattern_fc(self, data_str, split_str):
        '''fc for searching using first pattern'''
        if split_str:
            data_lst = data_str.split(split_str)
            if len(data_lst) > 1:
                output_str = split_str + split_str.join(data_lst[1:])
            else:
                output_str = None
            return output_str
        return None

    def _searchbynextpattern_fc(self, data_str, split_str, collectedpattern_str):
        '''fc for searching using next pattern after first'''
        if split_str:
            data_str = data_str[len(collectedpattern_str):]
            data_lst = data_str.split(split_str)
            if len(data_lst) > 1:
                collectedpattern_str += data_lst[0] + split_str
            else:
                collectedpattern_str = None
            return collectedpattern_str
        return None

    def findgran_fc(self, data_str, granpattern_str):
        '''logic for search start gran'''
        counter_int = 0
        collectedpattern_str = ''
        patterns_lst = self._convertgrantolist_fc(granpattern_str)
        while patterns_lst and isinstance(collectedpattern_str, str):
            split_str = patterns_lst.pop()
            print('OK - start search pattern:', split_str)
            if not counter_int:
                data_str = self._searchbyfirstpattern_fc(data_str, split_str)
                collectedpattern_str += split_str
            else:
                collectedpattern_str = self._searchbynextpattern_fc(data_str, split_str, collectedpattern_str)
            if not data_str:
                return None
            counter_int += 1
        return collectedpattern_str

    def parsewithgrans_fc(self, data_str, startgranpattern_str, finishgranpattern_str):
        '''fc for parsing usual gran'''
        startgran_str = self.findgran_fc(data_str, startgranpattern_str)
        data_lst = data_str.split(startgran_str)
        if len(data_lst) > 1 and startgran_str:
            data_str = startgran_str.join(data_lst[1:])
            finishgran_str = self.findgran_fc(data_str, finishgranpattern_str)
            if finishgranpattern_str:#maybe finishgran_str???
                snippet_str = data_str.split(finishgranpattern_str)[0]
                return (startgran_str, snippet_str, finishgran_str)
        return None

    def parsebyorder_fc(self, data_str, startgran_str, startgran_ordernr_int, finishgran_str, finishgran_ordernr_int):
        '''fc to parse snippet accordingly order of it'''
        data_lst = data_str.split(startgran_str)
        if len(data_lst) > 1 and startgran_ordernr_int + 1 < len(data_lst):
            data_str = startgran_str.join(data_lst[startgran_ordernr_int:])
        else:
            return None
        snippet_lst = data_str.split(finishgran_str)
        if len(snippet_lst) > 1 and finishgran_ordernr_int < len(snippet_lst):
            data_str = finishgran_str.join(snippet_lst[:finishgran_ordernr_int + 1])
        else:
            return None
        return data_str

    def parsewithgrans_loop_fc(self, data_str, startgranpattern_str, finishgranpattern_str):
        '''fc for parsing list of snippets'''
        output_lst = list()
        while True:
            #snippet_tuple = (startgran_str, parsedsnippet_str, finishgran_str)
            snippet_tuple = self.parsewithgrans_fc(data_str, startgranpattern_str, finishgranpattern_str)
            if snippet_tuple:
                output_lst.append(snippet_tuple)
            else:
                break
            snippet_str = ''.join(snippet_tuple)
            data_lst = data_str.split(snippet_str)
            if len(data_lst) > 1:
                data_str = snippet_str.join(data_lst[1:])
            else:
                data_str = data_lst[0]
        return output_lst


class Parser(Cdparser):
    looptitle_str = 'LOOP'
    startgrantitle_str = 'STARTGRAN'
    finishgrantitle_str = 'FINISHGRAN'

    def __init__(self, *args_tuple):
        self.__reset_fc()
        self.fieldtitles_tuple = args_tuple  # list of fields in output

    def __iteratebypayload_fc(self):
        '''fc for iteration payload of parsing settings and complete parsing process accordingly it'''
        for k, v in self.parserpayload_dc_dc.items():
            #search for loops
            if k == self.looptitle_str:
                startfinishgrans_dc = self.parserpayload_dc_dc.get(k)
                self.__parseloop_fc(**startfinishgrans_dc)
        #search for usual grans inside loop
        if len(self.fieldtitles_tuple):
            for title_str in self.fieldtitles_tuple:
                if isinstance(title_str, str):
                    startfinishgrans_dc = self.parserpayload_dc_dc.get(title_str)
                    if isinstance(startfinishgrans_dc, dict):
                        if len(self.parsedsnippets_lst) > 0:
                            for snippetnr_int, snippet_tuple in enumerate(self.parsedsnippets_lst):
                                #snippet_tuple structure is (startgran_str, valueparsed_str, finishgran_str)
                                snippet_str = ''.join(snippet_tuple)
                                snippet_tuple = self.__parseusualgran_fc(snippet_str, **startfinishgrans_dc)
                                #update data list with new values
                                snippetkey_str = str(snippetnr_int)
                                if snippetkey_str not in self.parseddata_dc_dc:
                                    self.parseddata_dc_dc.update({snippetkey_str:{}})
                                self.parseddata_dc_dc[snippetkey_str].update({title_str:snippet_tuple})
                        else:
                            snippet_tuple = self.__parseusualgran_fc(self.data_str, **startfinishgrans_dc)
                            snippetkey_str = '0'
                            if snippetkey_str not in self.parseddata_dc_dc:
                                self.parseddata_dc_dc.update({snippetkey_str: {}})
                            self.parseddata_dc_dc[snippetkey_str].update({title_str: snippet_tuple})

    def process_fc(self, data_str, **kwargs_dc_dc):
        '''decision tree of parsing process based on payloaded dictionay'''
        self.__reset_fc()
        self.data_str = data_str
        self.parserpayload_dc_dc = kwargs_dc_dc
        if isinstance(self.data_str, str):
            self.__iteratebypayload_fc()

    def __parseloop_fc(self, **startfinishgrans_dc):
        '''Parsing loop function'''
        stargran_payload_tuple = startfinishgrans_dc.get(self.startgrantitle_str)
        finishgran_payload_tuple = startfinishgrans_dc.get(self.finishgrantitle_str)
        startgran_str = stargran_payload_tuple[0]
        finishgran_str = finishgran_payload_tuple[0]
        self.parsedsnippets_lst = self.parsewithgrans_loop_fc(self.data_str, startgran_str, finishgran_str)
        print('OK - parsed snippets count is:', len(self.parsedsnippets_lst))

    def __parseusualgran_fc(self, data_str, **startfinishgrans_dc):
        """parsing usual gran function
        _payload_dc is: 'startgrantitle_str': ('startgranvalue_str', ordernumber_startgran_int),
        """
        print(startfinishgrans_dc)
        stargran_payload_tuple = startfinishgrans_dc.get(self.startgrantitle_str)
        finishgran_payload_tuple = startfinishgrans_dc.get(self.finishgrantitle_str)
        startgran_str = stargran_payload_tuple[0]
        finishgran_str = finishgran_payload_tuple[0]
        snippet_tuple = self.parsewithgrans_fc(data_str, startgran_str, finishgran_str)
        return snippet_tuple

    def getcleardata_fc(self):
        '''fc that extract data from parser obj'''
        output_dc_dc = dict()
        if self.parseddata_dc_dc:
            for snippetnr_str, snippet_dc in self.parseddata_dc_dc.items():
                if snippetnr_str not in output_dc_dc:
                    output_dc_dc.update({snippetnr_str:{}})
                for fieldtitle_str, data_tuple in snippet_dc.items():
                    output_dc_dc[snippetnr_str].update({fieldtitle_str:data_tuple[1]})
        return output_dc_dc

    def __reset_fc(self):
        self.data_str = None
        self.parserpayload_dc_dc = None
        self.parsedsnippets_lst = list()
        self.parseddata_dc_dc = dict()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        pass
    else:
        print('diag started...')
        sample_str = '''<p><p><h1>Andrei</h1></p></p><a href="fhkjdhf">ssylka</a>'''
        print('sample is:', sample_str)
        field1_str = 'title'
        parserpayloadloopexample_dc = {
            Parser.looptitle_str:{
                Parser.startgrantitle_str:('<', 0),
                Parser.finishgrantitle_str:('>', 0)
            },
            field1_str:{
                Parser.startgrantitle_str: ('<p>{skip}<h1>', 0),
                Parser.finishgrantitle_str: ('</h1>', 0)
            }
        }
        print(parserpayloadloopexample_dc)
        parser_obj = Parser(field1_str)
        parser_obj.process_fc(sample_str, **parserpayloadloopexample_dc)
        print('OK - collected {} elements:'.format(len(parser_obj.parsedsnippets_lst)), parser_obj.parsedsnippets_lst)
        print('OK - it is: ', parser_obj.parseddata_dc_dc)