import datetime
import pytz


def str_to_datetime(s: str, tz):
    dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
    dt = dt.astimezone(pytz.timezone(tz))
    return dt


def datetime_to_str(dt: datetime.datetime):
    return datetime.datetime.strftime(dt, "%Y-%m-%dT%H:%M:%S%z")
