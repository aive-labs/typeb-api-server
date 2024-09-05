from enum import Enum


class RepeatTypeEnum(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTER = "quarter"
    HALFYEAR = "half_year"
    YEARLY = "yearly"
