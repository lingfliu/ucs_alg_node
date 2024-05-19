class AlgTask:
    """algorithm task
    :param tid: int, task id
    :param ts: int, timestamp
    :param input: str, input data"""
    def __init__(self, tid, ts, input):
        self.alg = tid
        self.ts = ts
        self.input = input