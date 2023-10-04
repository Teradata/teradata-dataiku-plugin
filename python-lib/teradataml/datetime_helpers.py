import datetime
from dateutil import parser



def now_datetime():
    """
    Return timezone-aware now datetime object.

    Returns:
        datetime: Timezone-aware current time
    """
    return datetime.datetime.now(datetime.timezone.utc)


def datetime_plus_minutes(dt, minutes: float):
    """
    Adds some number of minutes to dt and returns result as a datetime object.

    Args:
        dt (datetime): Datetime object to add minutes to.
        minutes (float): Number of minutes to add. Can be negative.

    Returns:
        datetime: Result of adding minutes
    """
    return dt + datetime.timedelta(minutes=minutes)


def datetime_plus_seconds(dt, seconds: float):
    """
    Adds some number of seconds to dt and returns result as a datetime object.

    Args:
        dt (datetime): Datetime object to add seconds to.
        minutes (float): Number of seconds to add. Can be negative.

    Returns:
        datetime: Result of adding seconds
    """
    return dt + datetime.timedelta(seconds=seconds)



def datetime_from_iso_string(iso_string: str):
    """
    Converts an ISO string to a datetime object.

    Args:
        iso_string (str): Timestamp string to convert

    Returns:
        datetime: Converted datetime object
    """

    return parser.parse(iso_string)