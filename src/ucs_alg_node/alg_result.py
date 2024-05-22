class AlgResult:
    """algorithm task
    :param id: string, task id
    :param ts: int, timestamp in milliseconds
    :param sources: list of input data
    :param meta: dict, meta info for
    """
    def __init__(self, task_id, ts, vals=None, explain=""):
        self.task_id = id
        self.ts = ts
        self.vals = vals
        self.explain = explain
