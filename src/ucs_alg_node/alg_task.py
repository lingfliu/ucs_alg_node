class AlgTask:
    """algorithm task
    :param id: string, task id
    :param ts: int, timestamp in milliseconds
    :param sources: list of input data
    :param meta: dict, meta info for
    """
    def __init__(self, id, ts, sources=[], meta={}):
        self.id = id
        self.ts = ts
        self.sources = sources
        self.meta = meta