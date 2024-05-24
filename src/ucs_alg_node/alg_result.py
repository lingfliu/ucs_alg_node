class AlgResult:
    """algorithm task
    :param task_id: string, task id
    :param ts: int, timestamp in milliseconds
    :param vals: values
    :param explain: plaintext explain of results
    """
    def __init__(self, task_id, ts, vals=None, explain=""):
        self.task_id = task_id
        self.ts = ts
        self.vals = vals
        self.explain = explain
