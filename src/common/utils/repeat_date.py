import calendar
from datetime import datetime, timedelta
from typing import Literal

import pytz
from dateutil.relativedelta import relativedelta

from src.campaign.enums.repeat_type import RepeatTypeEnum


def get_last_day_of_month(date: datetime) -> int:
    """

    Args:
        date: date는 현재 날짜를 의미

    Returns: 현월의 마지막 날짜를 리턴
    """
    # monthrange 함수는 주어진 연도와 월에 대한 (첫 번째 요일, 마지막 날짜)를 반환
    return calendar.monthrange(date.year, date.month)[1]


def calculate_dates(
    start_date: datetime,
    period: RepeatTypeEnum,
    week_days: str | None = None,
    datetosend: Literal["end_of_month"] | int | None = None,
    timezone="UTC",
):
    # end_of_month -> 매월, 분기, 반기에만 말일이라는 필드가 존재

    # 타임존 설정
    tz = pytz.timezone(timezone)
    next_start = None

    if week_days is None:
        week_days = "0000000"

    if datetosend == "end_of_month":
        # 오늘 기준으로 해당 분기 말일
        datetosend = get_last_day_of_month(start_date)

    if datetosend is None:
        datetosend = 1

    if period == RepeatTypeEnum.DAILY:
        start = start_date + timedelta(days=1)
        end = start
        next_start = start + timedelta(days=1)

    elif period == RepeatTypeEnum.WEEKLY:
        if sum([int(day) for day in week_days]) == 0:
            raise ValueError("At least one day should be selected for weekly repeat")
        days_to_add = [int(day) for day in week_days]
        next_day = start_date
        while True:
            next_day += timedelta(days=1)
            if days_to_add[next_day.weekday()] == 1:
                break
        start = next_day
        end = start
        # 다음 시작일 찾기
        while True:
            next_day += timedelta(days=1)
            if days_to_add[next_day.weekday()] == 1:
                next_start = next_day
                break

    elif period == RepeatTypeEnum.MONTHLY:
        # start_date -> now

        if start_date.day < datetosend:
            start = start_date.replace(day=datetosend)
        else:
            # 다음달의 선택된 날짜
            start = (start_date + relativedelta(months=1)).replace(day=datetosend)

        end = start
        next_start = start + relativedelta(months=1)

    elif period == RepeatTypeEnum.QUARTER.value:
        if start_date.month in [1, 4, 7, 10] and start_date.day < datetosend:
            start = start_date.replace(day=datetosend)
        else:
            start = (start_date + relativedelta(months=3 - ((start_date.month - 1) % 3))).replace(
                day=datetosend
            )

        end = start
        next_start = start + relativedelta(months=3)

    elif period == RepeatTypeEnum.HALFYEAR:
        if start_date.month < 7 or (start_date.month == 7 and start_date.day < datetosend):
            start = (
                datetime(start_date.year, 1, datetosend, tzinfo=tz)
                if start_date.month >= 7
                else datetime(start_date.year, 7, datetosend, tzinfo=tz)
            )
        else:
            start = datetime(start_date.year + 1, 1, datetosend, tzinfo=tz)

        end = start
        next_start = datetime(
            start.year + (start.month // 7),
            7 if start.month < 7 else 1,
            datetosend,
            tzinfo=tz,
        )
    # 종료일은 다음 시작일의 전일로 설정
    start = start.strftime("%Y%m%d")
    end = (next_start - timedelta(days=1)).strftime("%Y%m%d")

    return start, end
