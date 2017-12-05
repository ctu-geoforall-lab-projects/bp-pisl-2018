import os
import logging

import json
import subprocess
import psycopg2
from osgeo import ogr, osr
from configparser import ConfigParser

from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.configuration import get_config_value
from pywps.validator.mode import MODE




class Process2(Process):
    def __init__(self):
        inputs=[LiteralInput('db_section', 'Input name of a database', data_type='string'),
                ComplexInput('buff_in', 'Input vector file',
                supported_formats=[Format('application/gml+xml')],
                mode=MODE.STRICT),
                LiteralInput('buffer', 'Buffer size', data_type='float',
                allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000))),
                ComplexInput('centr_in', 'Layer',
                supported_formats=[
                Format('application/gml+xml')])
        ]
        outputs=[LiteralOutput('buff_out', 'Buffered table', data_type='string'),
                LiteralOutput('centr_out', 'Centroids table', data_type='string')
        ]
        
        super(Process2, self).__init__(
            self._handler,
            identifier='Process2',
            title='The Buffer and Centroids processes merged together',
            abstract='The process _________',
            version='1.0',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,            
            status_supported=True
        )

    def _handler(self, request, response):
        self.user_input= request.inputs['db_section'][0].data
        
        self.setOutputDbStorage(self.user_input)
        
        inSource = ogr.Open(request.inputs['buff_in'][0].file)
        inLayer = inSource.GetLayer()
        out = inLayer.GetName() + '_buffer'

        # create output file
        driver = ogr.GetDriverByName('GML')
        outSource = driver.CreateDataSource(
                                out,
                                ["XSISCHEMAURI=\
                            http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayer = outSource.CreateLayer(out, None, ogr.wkbUnknown)

        # for each feature
        featureCount = inLayer.GetFeatureCount()
        index = 0

        while index < featureCount:
            from shapely.geometry import shape, mapping

            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(float(request.inputs['buffer'][0].data))

            # create output feature to the file
            outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()  # makes it crash when using debug
            index += 1
            response.update_status('Buffering', 100*(index/featureCount))

        outSource.Destroy()        
        # ogr2ogr requires gdal-bin
        input_gml = request.inputs['centr_in'][0].file
        input_geojson = 'input.geojson'
        subprocess.check_call(['ogr2ogr', '-f', 'geojson',
                               input_geojson, input_gml])
        with open(input_geojson, 'rb') as f:
            xxx = f.read() #zmeneno
            data = json.loads(xxx.decode('utf-8'))
        for feature in data['features']:
            geom = shape(feature['geometry'])
            feature['geometry'] = mapping(geom.centroid)
        out_bytes = json.dumps(data, indent=2)
        
        response.outputs['centr_out'].file = out_bytes        
        response.outputs["buff_out"].file = out  
        return response