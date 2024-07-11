from src.users.domain.user import User


class AuthorizationChecker:
    def __init__(self, user: User):
        self.user_id = user.user_id
        self.department_id = user.department_id
        self.role_id = user.role_id

    def object_role_access(self) -> bool:
        """
        1.admin
        2.operator
        """
        if self.role_id in ["admin", "operator"]:
            return True
        else:
            return False

    def object_department_access(self, campaign_obj) -> bool:
        """
        1.department
        """
        if campaign_obj.owned_by_dept == self.department_id:
            return True
        else:
            return False
