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


class ProcessTwoOutputs(Process):
    def __init__(self):
        inputs=[ComplexInput('poly_in', 'Input vector file',
                             supported_formats=[Format('application/gml+xml')],
                             mode=MODE.STRICT),
                LiteralInput('buffer', 'Buffer size', data_type='float',
                             allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000)))
        ]
        outputs = [ComplexOutput('buff_out', 'Buffered file',
                                 supported_formats=[
                                            Format('application/gml+xml')
                                            ]
                                 ),
                   ComplexOutput('centr_out', 'Centroud buffered file',
                                 supported_formats=[
                                     Format('application/gml+xml')
                                 ]
                   ),
        ]
        
        super(ProcessTwoOutputs, self).__init__(
            self._handler,
            identifier='process-two-outputs',
            title='Process with two vector outputs',
            abstract='Buffers around the input features and compute centroids using the GDAL library',
            version='1.0',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,            
            status_supported=True
        )

    def _handler(self, request, response):
        inSource = ogr.Open(request.inputs['poly_in'][0].file)
        inLayer = inSource.GetLayer()

        driver = ogr.GetDriverByName('GML')
        
        # create output buffer file
        outBuff = inLayer.GetName() + '_buffer'
        outSourceB = driver.CreateDataSource(
                                outBuff,
                                ["XSISCHEMAURI=\
                            http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayerB = outSourceB.CreateLayer(outBuff, None, ogr.wkbUnknown)

        # create output centroid file
        outCentr = inLayer.GetName() + '_centroid'

        outSourceC = driver.CreateDataSource(
                                outCentr,
                                ["XSISCHEMAURI=\
                            http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayerC = outSourceC.CreateLayer(outCentr, None, ogr.wkbUnknown)
        
        # for each feature
        featureCount = inLayer.GetFeatureCount()
        index = 0

        bsize = float(request.inputs['buffer'][0].data)
        
        while index < featureCount:
            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(bsize)

            centroid = buff.Centroid()
            
            # create output buffer feature to the file
            outFeature = ogr.Feature(feature_def=outLayerB.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayerB.CreateFeature(outFeature)
            outFeature.Destroy()  # makes it crash when using debug

            # create output centroid feature to the file
            outFeature = ogr.Feature(feature_def=outLayerC.GetLayerDefn())
            outFeature.SetGeometryDirectly(centroid)
            outLayerC.CreateFeature(outFeature)
            outFeature.Destroy()  # makes it crash when using debug
            
            index += 1
            response.update_status('Buffering', 100*(index/featureCount))

        outSourceB.Destroy()
        outSourceC.Destroy()        

        response.outputs['buff_out'].output_format = FORMATS.GML
        response.outputs["buff_out"].file = outBuff
        response.outputs['centr_out'].output_format = FORMATS.GML
        response.outputs['centr_out'].file = outCentr
        
        return response
