from enum import Enum


class GAScriptStatus(Enum):
    PENDING = "pending"
    COPIED = "copied"
    VERIFYING = "verifying"
    COMPLETED = "completed"
