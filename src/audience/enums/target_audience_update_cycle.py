from enum import Enum


class TargetAudienceUpdateCycle(Enum):
    SKIP = "skip"  ## Do-not-update
    PRE_EXECUTION = "pre_execution"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
