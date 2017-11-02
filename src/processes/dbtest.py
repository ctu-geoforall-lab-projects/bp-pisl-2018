import os

import psycopg2
from configparser import ConfigParser

from pywps import Process, LiteralInput, LiteralOutput


class DbTest(Process):
	def __init__(self):
		inputs=[LiteralInput('dbname', 'Input name of a database', data_type='string')]
		outputs=[LiteralOutput('response', 'Output response', data_type='string')]
		
		super(DbTest, self).__init__(
            self._handler,
            identifier='DbTest',
            title='Testing database connection',
            abstract='Returns either a "Success" or "Fail" message depending on whether the database connection was established',
            version='1.3.3.7',
            inputs=inputs,
            outputs=outputs,
			store_supported=True,            #nejsem si jisty, k cemu tohle je 
            status_supported=True
			
		)

	def db_connect(self):
		cfg_file = os.path.join(os.path.dirname(__file__), '..', 'pywps.cfg')
		config = ConfigParser()
		config.read(cfg_file)
		if 'db' not in config.keys():
			raise Exception("Failed reading DB connection settings")

		return config['db']

	def _handler(self, request, response):
		user_input= request.inputs['dbname'][0].data
		conn = self.db_connect()
		try:
			conn = psycopg2.connect(
                                "dbname={} user={} password={} host={}".format(
                                        user_input, conn['user'], conn['password'], conn['host']
                        ))
			response.outputs['response'].data = "Success"
		except:
			response.outputs['response'].data = "Fail"
		return response
