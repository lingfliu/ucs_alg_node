import threading

from src.ucs_alg_node.utils import StoppableThread, InteruptableThread

STAT_INIT = 'init' # alg is initiating (model loading, etc.)
STAT_IDLE = 'idle' # alg is idle
STAT_RUNNING = 'running' # alg is running
STAT_ERR = 'error' # alg is in error state


class Alg:
    def __init__(self, mode='stream', model=None, task=None):
        """
        :param mode: str, 'stream' or 'batch'
        :param sources: list, data sources if in stream mode
        :param model: str, model name or file path
        """
        self.mode = mode
        self.model = model

        self.task = task # const in stream mode, variable in batch mode

    def init(self):
        """prepare algorithm: loading model, parameter initialization"""
        res = self.load_model()
        if res < 0:
            print('load model failed')
            return -1

        res = self.prepare()
        if res < 0:
            print('alg prepar error')
            return -1

        return 0

    def prepare(self):
        """algorithm preparation
        implement this
        """
        return 0

    def load_model(self):
        """
        load model locally or remotely
        :return: 0 if success, -1 if failed
        """
        return 0

    def infer_stream(self):
        """stream infer
        1. iteratively read data from the sources
        2. put into the inferencer
        3. return the results
        """
        yield None

    def infer_batch(self, task):
        """batch infer, must have input data
        :return: result
        """
        self.task = task

    def reload(self):
        """reload algorithm by cleaning the caches"""
        # 1. clean the caches
        # 2. reconfig the algorithm
        # 3. reset algorithm
        self.cleanup()
        # reinit
        self.init()

    def cleanup(self):
        """TODO: clean buffs, state"""
        pass



