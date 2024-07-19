from datetime import datetime, timedelta

import pytz

from src.campaign.enums.message_send_type import MessageSendType


def get_localtime():
    local_timezone = pytz.timezone("Asia/Seoul")
    datetime_now = datetime.now(local_timezone)
    return datetime_now


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


def get_unix_timestamp() -> int:
    # datetime 객체를 Unix 시간 (마이크로초 단위)로 변환
    now = datetime.now()
    return int(now.timestamp() * 1_000_000)


def convert_str_iso_8601_to_datetime(date_str: str):
    # data_str
    # 주어진 날짜 문자열 포맷 "2017-12-19T14:39:22+09:00"
    return datetime.fromisoformat(date_str)


def convert_datetime_to_iso8601(date):
    """
    Converts a datetime object to an ISO8601 formatted string.

    Parameters:
    dt (datetime): The datetime object to convert.

    Returns:
    str: The ISO8601 formatted string.
    """
    tz = pytz.timezone("Asia/Seoul")
    date = date.astimezone(tz)
    return date.isoformat(timespec="seconds")


def convert_datetime_to_iso8601_with_timezone(date):
    """
    Converts a datetime object to an ISO8601 formatted string.

    Parameters:
    dt (datetime): The datetime object to convert.

    Returns:
    str: The ISO8601 formatted string.
    """
    tz = pytz.timezone("Asia/Seoul")
    date = date.astimezone(tz)
    return date.isoformat(timespec="seconds")


def get_reservation_date(msg_send_type, start_date, send_date, remind_date):
    if msg_send_type == MessageSendType.CAMPAIGN.value:
        if send_date:
            resv_date = send_date
        else:
            resv_date = start_date

    elif msg_send_type == MessageSendType.REMIND.value:
        resv_date = remind_date

    return resv_date
