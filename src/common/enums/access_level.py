from enum import Enum


class AccessLevel(Enum):
    admin = 1
    operator = 10
    user = 20
    branch_user = 30
