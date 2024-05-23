import datetime
def current_time_milli():
    dt = datetime.datetime.now()
    return dt.microsecond / 1000