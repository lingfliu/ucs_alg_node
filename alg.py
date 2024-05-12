class Alg:
    '''a synchronous algorithm framework'''

    def __init__(self, mode='stream', sources=None, model=None, submit=None):
        self.sources = sources
        self.model = model
        self.submit = submit

    def infer_stream(self):
        '''stream infer'''
        pass

    def infer_batch(self, data=None):
        '''batch infer, must input data'''
        if not data:
            return -1

    def reload(self):
        '''reload algorithm by cleaning the caches'''
        pass

