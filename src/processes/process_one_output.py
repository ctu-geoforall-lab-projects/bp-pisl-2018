import os
import logging

import psycopg2
from osgeo import ogr, osr
from configparser import ConfigParser

from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.configuration import get_config_value
from pywps.validator.mode import MODE

class ProcessOneOutput(Process):
    def __init__(self):
        inputs=[LiteralInput('db_section', 'Database section', data_type='string'),
                ComplexInput('poly_in', 'Input vector file',
                supported_formats=[Format('application/gml+xml')],
                mode=MODE.STRICT),
                LiteralInput('buffer', 'Buffer size', data_type='float',
                allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000)))
        ]
        outputs=[LiteralOutput('buff_out', 'Output buffer table name', data_type='string')
        ]
        
        super(ProcessOneOutput, self).__init__(
            self._handler,
            identifier='process-one-output',
            title='Process with one vector output',
            abstract='Buffers around the input features using the GDAL library',
            version='1.0',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,            
            status_supported=True
        )

    def _handler(self, request, response):
        dbsection = request.inputs['db_section'][0].data
        self.setOutputDbStorage(dbsection)
        
        inSource = ogr.Open(request.inputs['poly_in'][0].file)
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

        bsize = float(request.inputs['buffer'][0].data)
        while index < featureCount:
            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(bsize)

            # create output feature to the file
            outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()  # makes it crash when using debug
            index += 1
            response.update_status('Buffering', 100*(index/featureCount))

        outSource.Destroy()
        
        response.outputs["buff_out"].file = out  
        return response
