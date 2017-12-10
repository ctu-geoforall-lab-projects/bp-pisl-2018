import requests
import xml.etree.ElementTree as ET

while True:
    process_number = int(input("Please enter 0 for process-no-output, 1 for process-one-output and 2 for process-two-outputs: "))
    if process_number == 0:
        URL = "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-no-output&datainputs=name=xxx"
        break
    elif process_number == 1:
        URL = "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-one-output&datainputs=db_section=db;poly_in=@xlink:href=http://127.0.0.1:5000/static/data/points.gml;buffer=10"
        break
    elif process_number == 2:
        URL = "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-two-outputs&datainputs=db_section=db;poly_in=@xlink:href=http://127.0.0.1:5000/static/data/points.gml;buffer=10"
        break
    else:
        print("Input Error")

response = requests.get(URL)
tree = ET.ElementTree(response)
root = ET.fromstring(response.content)

identifier = root[0][0].text
string = root[2][0][2][0].text

if type(string) != str:
    raise Exception("Not a string.")
    
if identifier != 'process-no-output':
    table1_name =(string.split(sep="."))
    if len(table1_name) != 3:
        raise Exception("Buffered table name does not consist of 3 parts separated by a dot.")
    if identifier == 'process-two-outputs':
        string2 = root[2][1][2][0].text
        table2_name = (string2.split(sep="."))
        if len(table2_name) != 3:
            raise Exception("Centroids table name does not consist of 3 parts separated by a dot.")




