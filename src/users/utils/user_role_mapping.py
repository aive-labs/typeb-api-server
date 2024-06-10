from src.users.domain.user_role import UserRole


def get_user_role_from_mapping(role: str) -> UserRole:
    role_mapping = {
        "admin": ("admin", "관리자"),
        "operator": ("operator", "운영자"),
        "user": ("user", "본사 사용자"),
        "branch_user": ("branch_user", "매장 사용자"),
    }

    if role not in role_mapping:
        raise ValueError("Invalid role provided")

    role_id, role_name = role_mapping[role]
    return UserRole(role_id=role_id, role_name=role_name)
