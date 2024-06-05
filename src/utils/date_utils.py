from datetime import datetime, timedelta

import pytz


def localtime_converter():
    local_timezone = pytz.timezone("Asia/Seoul")
    datetime_now = datetime.now(local_timezone)
    return datetime_now.isoformat()


def localtime_from_str(datetime_string: str):
    local_timezone = pytz.timezone("Asia/Seoul")
    datetime_now = datetime.fromisoformat(datetime_string.replace("Z", "+00:00"))
    datetime_object_utc = datetime_now.replace(tzinfo=pytz.utc)
    datetime_object = datetime_object_utc.astimezone(local_timezone)
    return datetime_object.isoformat()


def calculate_remind_date(end_date, remind_duration):
    end_date = datetime.strptime(end_date, "%Y%m%d")
    remind_duration_days = timedelta(days=remind_duration)
    result_date = end_date - remind_duration_days
    remind_date = result_date.strftime("%Y%m%d")

    return remind_date
