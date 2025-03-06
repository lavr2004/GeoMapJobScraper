from bin.loader import Loader
from bin.parser import Parser

url_str = 'https://shearman.wd1.myworkdayjobs.com/en-US/ShearmanandSterling/0/searchPagination/318c8bb6f553100021d223d9780d30be/0'

loader_obj = Loader()
data_str = loader_obj.process_loadstring_fc(url_str)
print(data_str)

field_title_str = 'title'
field_ref_str = 'ref'
field_url_str = 'url'
field_location_str = 'location'
field_date_str = 'date'
field_evidence_str = 'evidence'

fields_lst = [field_title_str, field_ref_str, field_url_str, field_location_str, field_date_str, field_evidence_str]

myworkdayjobs_payload_dc = {
    Parser.looptitle_str:{
        Parser.startgrantitle_str:('"widget":"templatedListItem","', 0),
        Parser.finishgrantitle_str:(']}', 0)
    },
    field_title_str:{
        Parser.startgrantitle_str:(',"instances":{skip}"text":"', 0),
        Parser.finishgrantitle_str:('","', 0)
    },
    field_ref_str:{
        Parser.startgrantitle_str:('.jobRequisitionId","instances":{skip}"text":"', 0),
        Parser.finishgrantitle_str:('"', 0),
    },
    field_url_str:{
        Parser.startgrantitle_str:('"commandLink":"', 0),
        Parser.finishgrantitle_str:('","', 0),
    },
    field_location_str: {
        Parser.startgrantitle_str: ('.locationsText","instances":{skip},"text":"', 0),
        Parser.finishgrantitle_str: ('"', 0),
    },
    field_date_str: {
        Parser.startgrantitle_str: ('.postedOn","instances":{skip}","text":"', 0),
        Parser.finishgrantitle_str: ('"', 0),
    },
    field_evidence_str: {
        Parser.startgrantitle_str: ('.jobRequisitionId{skip}"text":"', 0),
        Parser.finishgrantitle_str: ('"'),
    },
}

parser_obj = Parser(*fields_lst)
parser_obj.process_fc(data_str, **myworkdayjobs_payload_dc)
datacollected_dc_dc = parser_obj.getcleardata_fc()

def convertdctocsv_fc(datatype_str, datacollected_dc_dc):
    outputdata_str = ''
    if datacollected_dc_dc:
        for snippetnr_int, snippetdata_dc in datacollected_dc_dc.items():
            outputdata_str += datatype_str + ';'
            for field_str in fields_lst:
                value_str = snippetdata_dc.get(field_str)
                if not value_str:
                    value_str = ''
                outputdata_str += value_str + ';'
            outputdata_str += '\n'
    return outputdata_str

outputdata_str = convertdctocsv_fc('mwdj', datacollected_dc_dc)

with open('datacollected.csv', 'w', encoding='utf-8-sig', errors='ignore') as fw:
    fw.write(outputdata_str)

print(outputdata_str)
# print('OK - collected snippets {}:'.format(len(parser_obj.parsedsnippets_lst)), parser_obj.parsedsnippets_lst)
# print('-' * 20)
# print('OK - collected data: ', parser_obj.parseddata_dc_dc)