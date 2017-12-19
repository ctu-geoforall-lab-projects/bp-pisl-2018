#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET

from osgeo import ogr

def parse_string(value):
    if len(value.split(sep=".")) != 3:
        raise Exception("Table name does not consist of 3 parts separated by a dot.")

def get_value(node, idx=0):
    try:
        value = node[2][idx][2][0].text
    except IndexError:
        raise Exception("No output value found (process probably failed)")

    if type(value) != str:
        raise Exception("Output value is not a string.")

    return value

def get_connstr():
    pass # PG:dbname=...

def check_output(value, refcount, reftype):
    db, idsch, table = value.split('.')
    ident, schema = idsch.split('_')

    dsn = ogr.Open(get_connstr())
    if dsn is None:
        raise Exception("")
    lyr = dsn.GetLayerByName('{}.{}'.format(schema, table))
    if lyr is None:
        raise Exception("")
    count = lyr.GetFeatureCount()
    if count != refcount:
        raise None
    # type vs reftype

def get_refcount(uri):
    dsn = ogr.Open('/vsicurl/{}'.format(data))
    # ...
    lyr = dsn.GetLayer()
    # ...

    return lyr.GetFeatureCount()
    
def run_process(URL, refcount):
    response = requests.get(URL)
    tree = ET.ElementTree(response)
    root = ET.fromstring(response.content)

    identifier = root[0][0].text
    print ("Process: {}".format(identifier))
    
    value = get_value(root)

    if identifier != 'process-no-output':
        parse_string(value)
        #check_output(value, refcount, ogr.wkbPolygon)
        
    if identifier == 'process-two-outputs':
        value2 = get_value(root, idx=1)
        parse_string(value2)
        #check_output(value, refcount, ogr.wkbPoint)

if __name__ == "__main__":
    data = "http://127.0.0.1:5000/static/data/points.gml"

    refcount = get_refcount(data)
    
    for URL in ["http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-no-output&datainputs=name=xxx",
                "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-one-output&datainputs=db_section=db;poly_in=@xlink:href={};buffer=10".format(data),
                "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-two-outputs&datainputs=db_section=db;poly_in=@xlink:href={};buffer=10".format(data)]:
        run_process(URL, refcount)


