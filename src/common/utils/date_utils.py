import random
from datetime import datetime, timedelta

import pytz

from src.campaign.enums.message_send_type import MessageSendType
from src.main.exceptions.exceptions import ConsistencyException


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
    local_timezone = pytz.timezone("Asia/Seoul")

    # 현재 날짜와 시간을 한국 타임존으로 가져오기
    now = datetime.now(local_timezone)
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

    # 초와 밀리세컨드 랜덤 생성
    random_seconds = random.randint(0, 59)
    random_milliseconds = random.randint(0, 999)
    datetime_obj = datetime_obj.replace(
        second=random_seconds, microsecond=random_milliseconds * 1000
    )

    datetime_obj -= timedelta(hours=9)

    formatted_date_str = datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    return formatted_date_str


def get_korean_current_datetime_yyyymmddhh24mims():
    local_timezone = pytz.timezone("Asia/Seoul")

    # 현재 날짜와 시간을 한국 타임존으로 가져오기
    now = datetime.now(local_timezone)

    # YYYYMMDDHH24MI 형식으로 포맷팅
    formatted_datetime = now.strftime("%Y%m%d%H%M%S%f")[:-3]

    return formatted_datetime


def get_expired_at_to_iso_format_kr_time(minutes: int):
    # 현재 시간
    local_timezone = pytz.timezone("Asia/Seoul")
    current_time = datetime.now(local_timezone)
    # 입력 받은 minutes 후 시간 계산
    future_time = current_time + timedelta(minutes=minutes) - timedelta(seconds=10)

    # ISO 8601 형식으로 출력
    iso_format_time = future_time.isoformat()

    return iso_format_time


def format_datetime(date_str):
    """
    주어진 날짜 문자열을 'YYYY-MM-DD HH:MM:SS' 형식으로 변환합니다.

    :param date_str: 변환할 날짜 문자열
    :return: 변환된 날짜 문자열
    """
    # 문자열을 datetime 객체로 변환
    date_obj = datetime.fromisoformat(date_str)

    # 원하는 포맷으로 변환
    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date
