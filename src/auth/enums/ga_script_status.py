from enum import Enum


class GAScriptStatus(Enum):
    PENDING = "pending"
    VERIFYING = "verifying"
    COMPLETED = "completed"
