STAT_INIT = 'init' # alg is initiating (model loading, etc.)
STAT_IDLE = 'idle' # alg is idle
STAT_RUNNING = 'running' # alg is running
STAT_ERR = 'error' # alg is in error state


class Alg:
    """a synchronous algorithm wrapper
    :param mode: str, 'stream' or 'batch'
    :param sources: list, data sources if in stream mode
    """

    def __init__(self, mode='stream', sources=None, model=None):
        self.mode = mode
        self.sources = sources
        self.model = model
        self.is_running = True # to break in stream mode

    def prepare(self):
        """prepare algorithm: loading model, parameter initialization"""
        self.load_model()
        self.init()

    def infer_stream(self):
        """stream infer
        1. iteratively read data from the sources
        2. put into the inferencer
        3. return the results
        """
        yield None

    def infer_batch(self, data=None):
        """batch infer, must input data"""
        if not data:
            return None

        return None

    def reload(self):
        """reload algorithm by cleaning the caches"""
        # 1. clean the caches
        # 2. reconfig the algorithm
        # 3. reset algorithm
        self.stop()
        self.cleanup()
        self.load_model()
        self.init()

    def cleanup(self):
        pass

    def load_model(self):
        """
        load model locally or remotely
        preferably, load model in async mode
        """
        pass

    def init(self):
        """parameter initialization """
        pass

    def stop(self):
        pass
