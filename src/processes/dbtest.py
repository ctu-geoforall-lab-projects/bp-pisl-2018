from pywps import Process, LiteralInput, LiteralOutput
import psycopg2

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
	
	def _handler(self, request, response):
		user_input= request.inputs['dbname'][0].data
		try:
			conn = psycopg2.connect("dbname=" + user_input + " user=pisl password=bakalarka host=geo102.fsv.cvut.cz")
			response.outputs['response'].data = "Success"
		except:
			response.outputs['response'].data = "Fail"
		return response
	

	
