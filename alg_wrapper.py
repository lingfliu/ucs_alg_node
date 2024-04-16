class AlgWrapper:
    def __init__(self, alg, source=None, mode='stream'):
        self.alg = alg
        self.mode = mode
        self.source = source


    def infer(self, data=None):
        if self.source and self.mode == 'stream':
            for data in self.source:
                yield self.alg.infer(data)
        elif self.mode == 'batch' and data:
            yield self.alg.infer(data)
        else:
            yield None