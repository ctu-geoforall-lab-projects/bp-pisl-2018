from pywps import Process, LiteralInput, LiteralOutput, UOM

class ProcessNoOutput(Process):
    def __init__(self):
        inputs = [LiteralInput('name', 'Input name', data_type='string')]
        outputs = [LiteralOutput('response',
                                 'Output response', data_type='string')]

        super(ProcessNoOutput, self).__init__(
            self._handler,
            identifier='process-no-output',
            title='Process with no vector output',
            abstract='Returns a literal string output with Hello plus the inputed name',
            version='1',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['response'].data = 'Hello ' + request.inputs['name'][0].data
        response.outputs['response'].uom = UOM('unity')
        return response
