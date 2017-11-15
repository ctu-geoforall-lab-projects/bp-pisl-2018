import os
import logging

import psycopg2
from osgeo import ogr, osr
from configparser import ConfigParser

from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.configuration import get_config_value
from pywps.validator.mode import MODE


class DbTest(Process):
    def __init__(self):
        inputs=[LiteralInput('dbname', 'Input name of a database', data_type='string'),
                ComplexInput('poly_in', 'Input vector file',
                supported_formats=[Format('application/gml+xml')],
                mode=MODE.STRICT),
                LiteralInput('buffer', 'Buffer size', data_type='float',
                allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000)))
        ]

        # outputs=[ComplexOutput('buff_out', 'Buffered file',
        #                      supported_formats=[Format('application/gml+xml')])
        # ]
        outputs=[LiteralOutput('buff_out', 'Buffered table', data_type='string')
        ]
        
        super(DbTest, self).__init__(
            self._handler,
            identifier='DbTest',
            title='Testing database connection and Buffer process',
            abstract='The process connects to a database and also returns buffers around the input features using the GDAL library',
            version='1.0',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,            
            status_supported=True
        )

    def unique_schema(self):
        return '{}_{}'.format(self.identifier.lower(),
                              str(self.uuid).replace("-", "_").lower()
        )

    def dbconnect(self):
        return "dbname={} user={} password={} host={}".format(
            self.user_input,
            get_config_value("db" , "user"), 
            get_config_value("db" , "password"),
            get_config_value("db" , "host"),
        )

    def store_output_db(self, layer):
        connstr = self.dbconnect()
        #        try:
        logging.debug("Connect string: {}".format(connstr))
        dsc = ogr.Open("PG:" + connstr)
        if dsc is None:
            raise Exception("Database connection has not been established.")
        layer = dsc.CopyLayer(layer, "buff_out", ['OVERWRITE=YES',
                                                  'SCHEMA={}'.format(self.unique_schema())]
        )
        # TODO: layer is valid even copying failed (schema do not exists)
        if layer is None:
            raise Exception("Writing output data to database failed.")

    def _handler(self, request, response):
        self.user_input= request.inputs['dbname'][0].data    #co znamena [0]?
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

        while index < featureCount:
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

        for param in response.outputs.keys():
            outSource = ogr.Open(out) # ???
            self.store_output_db(outSource.GetLayer())
            outSource.Destroy()
        
            #        response.outputs['buff_out'].output_format = FORMATS.GML
            response.outputs[param].data = '{}.{}.{}'.format(self.user_input, self.unique_schema(), param)

        return response
