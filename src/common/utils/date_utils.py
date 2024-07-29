from datetime import datetime, timedelta, timezone

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
    else:
        raise ConsistencyException(detail={"발송 날짜가 존재하지 않습니다."})

    return resv_date


def create_logical_date_for_airflow(date_str: str, time_str: str) -> str:
    """
    주어진 날짜와 시간을 UTC+9 시간대의 ISO 8601 형식의 문자열로 변환하는 함수.

    :param date_str: 날짜 문자열 (형식: YYYYMMDD)
    :param time_str: 시간 문자열 (형식: HH:MM)
    :return: UTC+9 시간대의 ISO 8601 형식의 문자열
    """
    # 날짜와 시간을 합쳐서 datetime 객체로 변환
    datetime_str = date_str + " " + time_str
    datetime_obj = datetime.strptime(datetime_str, "%Y%m%d %H:%M")

    # UTC+9 시간대로 변환
    utc_plus_9 = timezone(timedelta(hours=9))
    datetime_obj = datetime_obj.replace(tzinfo=utc_plus_9)

    # ISO 8601 형식의 문자열로 변환
    iso_format_str = datetime_obj.isoformat()

    return iso_format_str


def get_current_datetime_yyyymmddhh24mi():
    # 현재 날짜와 시간 가져오기
    now = datetime.now()

    # YYYYMMDDHH24MI 형식으로 포맷팅
    formatted_datetime = now.strftime("%Y%m%d%H%M")

    return formatted_datetime
