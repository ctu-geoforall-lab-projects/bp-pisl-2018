#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from pywps.configuration import get_config_value, load_configuration
from osgeo import ogr, osr

load_configuration(['pywps.cfg'])


def parse_string(value):
    if len(value.split(sep=".")) != 3:
        raise Exception("Table name does not consist of 3 parts separated by dots.")

def get_value(node, idx=0):
    try:
        value = node[2][idx][2][0].text
    except IndexError:
        raise Exception("No output value found (process probably failed)")

    if type(value) != str:
        raise Exception("Output value is not a string.")

    return value

def get_connstr():
    connstr = "PG:dbname={} user={} password={} host={}".format(
            get_config_value("db", "dbname"),
            get_config_value("db", "user"), 
            get_config_value("db", "password"),
            get_config_value("db", "host")
        )
    return(connstr)
    
def check_output(value, refcount, reftype):
    db, idsch, table = value.split('.')
    ident, schema = idsch.split('_')

    dsn = ogr.Open(get_connstr())
    if dsn is None:
        raise Exception("Reading data failed.")
    print('{}.{}'.format(schema, table))
    print('{}.{}'.format(idsch, table))
    #prepsal jsem '{}.{}'.format(schema, table) na '{}.{}'.format(idsch, table), protoze schema (viz QGIS) je cely ten idsch
    lyr = dsn.GetLayerByName('{}.{}'.format(idsch, table))
    if lyr is None:
        raise Exception("Could not find the layer.")
    count = lyr.GetFeatureCount()
    print(count)
    print(refcount)
    if count != refcount:
        raise Exception("The number of elements written to the database is different from the number of elements in the input file.")
    # type vs reftype
    type = ogr.CreateGeometryFromWkb(lyr)
    if type != reftype:
        raise Exception("Geometry of the  different from the number of elements written to the database.")


def get_refcount(uri):
    dsn = ogr.Open('/vsicurl/{}'.format(data))
    if dsn is None:
        raise Exception("Reading data failed. (get_refcount)")
    lyr = dsn.GetLayer()
    if lyr is None:
        raise Exception("Could not find the layer. (get_refcount)")
    

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
        check_output(value, refcount, ogr.wkbPolygon)
        
    if identifier == 'process-two-outputs':
        value2 = get_value(root, idx=1)
        parse_string(value2)
        check_output(value, refcount, ogr.wkbPoint)

if __name__ == "__main__":
    data = "http://127.0.0.1:5000/static/data/points.gml"
    #data = "http://rain.fsv.cvut.cz/geodata/test.gml"
    refcount = get_refcount(data)
    
    for URL in ["http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-no-output&datainputs=name=xxx",
                "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-one-output&datainputs=db_section=db;poly_in=@xlink:href={};buffer=10".format(data),
                "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-two-outputs&datainputs=db_section=db;poly_in=@xlink:href={};buffer=10".format(data)]:
        run_process(URL, refcount)


