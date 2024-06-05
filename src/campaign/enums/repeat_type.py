from enum import Enum


class RepeatType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTER = "quarter"
    HALFYEAR = "half_year"
    YEARLY = "yearly"
