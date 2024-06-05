import calendar
from datetime import datetime, timedelta
from typing import Literal

import pytz
from dateutil.relativedelta import relativedelta

from src.campaign.enums.repeat_type import RepeatType


def get_last_day_of_month(date: datetime):
    year = date.year
    month = date.month

    # monthrange 함수는 주어진 연도와 월에 대한 (첫 번째 요일, 마지막 날짜)를 반환
    last_day = calendar.monthrange(year, month)[1]
    return last_day


def calculate_dates(
    start_date: datetime,
    period,
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

    if datetosend is None:
        datetosend = 1

    if period == RepeatType.DAILY.value:
        start = start_date + timedelta(days=1)
        end = start
        next_start = start + timedelta(days=1)

    elif period == RepeatType.WEEKLY.value:
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

    elif period == RepeatType.MONTHLY.value:
        # start_date -> now

        if datetosend == "end_of_month":
            # 이번달 말일
            last_day_of_month = get_last_day_of_month(start_date)
            start = start_date.replace(day=last_day_of_month)
        else:
            if start_date.day < datetosend:
                start = start_date.replace(day=datetosend)
            else:
                # 다음달의 선택된 날짜
                start = (start_date + relativedelta(months=1)).replace(day=datetosend)

        end = start
        next_start = start + relativedelta(months=1)

    elif period == RepeatType.QUARTER.value:
        # TODO
        if datetosend == "end_of_month":
            # 오늘 기준으로 해당 분기 말일

            for month in [1, 4, 7, 10]:
                if start_date.month <= month:
                    break

            last_day_of_month = get_last_day_of_month(start_date)
            pass

        else:
            if start_date.month in [1, 4, 7, 10] and start_date.day < datetosend:
                start = start_date.replace(day=datetosend)
            else:
                start = (
                    start_date + relativedelta(months=3 - ((start_date.month - 1) % 3))
                ).replace(day=datetosend)
        end = start
        next_start = start + relativedelta(months=3)

    elif period == RepeatType.HALFYEAR.value:

        # TODO
        if datetosend == "end_of_month":
            pass
            # 오늘 기준으로 반기 말일?
        else:
            if start_date.month < 7 or (
                start_date.month == 7 and start_date.day < datetosend
            ):
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

    # TODO
    # 종료일은 다음 시작일의 전일로 설정
    start = start.strftime("%Y%m%d")
    end = (next_start - timedelta(days=1)).strftime("%Y%m%d")

    return start, end
