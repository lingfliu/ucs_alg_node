class Alg:
    '''a synchronous algorithm framework'''

    def __init__(self):
        pass

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

