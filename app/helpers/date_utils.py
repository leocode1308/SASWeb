import datetime

def time_stamp_to_datetime(timestamp):
    """
    Convert a Unix timestamp to a datetime object.
    
    :param timestamp: Unix timestamp (seconds since epoch)
    :return: datetime object
    """
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)