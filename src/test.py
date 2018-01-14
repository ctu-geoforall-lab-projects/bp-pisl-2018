#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from pywps.configuration import get_config_value, load_configuration
from osgeo import ogr, osr

load_configuration(['pywps.cfg'])


def parse_string(value):
    if len(value.split(sep=".")) != 3:
        raise Exception("Table name does not consist of 3 parts separated by dots.")

def get_value(node, identifier='response'):
    value = None
    try:
        xlink_key = '{http://www.w3.org/1999/xlink}href'
        po_node = node.find('{http://www.opengis.net/wps/1.0.0}ProcessOutputs')
        for n in po_node.findall('{http://www.opengis.net/wps/1.0.0}Output'):
            if n.find('{http://www.opengis.net/ows/1.1}Identifier').text == identifier:
                if identifier == 'response':
                    value = n.find('{http://www.opengis.net/wps/1.0.0}Data').text
                    break
                else:
                    ref_node = n.find('{http://www.opengis.net/wps/1.0.0}Reference')
                    value = ref_node.attrib['{http://www.w3.org/1999/xlink}href']
                    break
    except IndexError:
        raise Exception("No output value found (process probably failed)")

    if value and type(value) != str:
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
    db, schema, table = value.split('.')

    dsn = ogr.Open(get_connstr())
    if dsn is None:
        raise Exception("Reading data failed.")
    lyr = dsn.GetLayerByName('{}.{}'.format(schema.replace('"', ''), table.replace('"', '')))
    if lyr is None:
        raise Exception("Could not find the layer {}.{}.".format(schema, table))
    count = lyr.GetFeatureCount()
    if count != refcount:
        raise Exception("Layer {}.{}: number of features differs (database: {} vs. input file: {})".format(schema, table, count, refcount))
    # type vs reftype
    gtype = lyr.GetGeomType()
    if gtype != reftype:
        raise Exception("Layer {}.{}: geometry type differs (database: {} vs. input file: {})".format(schema, table, gtype, reftype))


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
        value = get_value(root, identifier='buff_out')
        parse_string(value)
        check_output(value, refcount, ogr.wkbPolygon)

    elif identifier == 'process-two-outputs':
        value2 = get_value(root, identifier='centr_out')
        parse_string(value2)
        check_output(value2, refcount, ogr.wkbPoint)

if __name__ == "__main__":
    data = "http://127.0.0.1:5000/static/data/points.gml"
    #data = "http://rain.fsv.cvut.cz/geodata/test.gml"
    refcount = get_refcount(data)
    
    for URL in ["http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-no-output&datainputs=name=xxx",
                "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-one-output&datainputs=poly_in=@xlink:href={};buffer=10&ResponseDocument=buff_out=@asReference=true".format(data),
                "http://127.0.0.1:5000/wps?service=wps&&version=1.0.0&request=execute&identifier=process-two-outputs&datainputs=poly_in=@xlink:href={};buffer=10&ResponseDocument=buff_out=@asReference=true;centr_out=@asReference=true".format(data)]:
        run_process(URL, refcount)


