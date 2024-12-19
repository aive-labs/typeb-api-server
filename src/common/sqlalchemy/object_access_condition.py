from sqlalchemy import or_

from src.common.model.role import RoleEnum
from src.user.infra.entity.user_entity import UserEntity


def object_access_condition(db, user, model):
    """Checks if the user has the required permissions for Object access.
       Return conditions based on object access permissions

    Args:
        dep: The object obtained from the `verify_user` dependency.
        model: Object Model
    """
    admin_access = (
        True if user.role_id in [RoleEnum.ADMIN.value, RoleEnum.OPERATOR.value] else False
    )

    if admin_access:
        res_cond = []
    else:
        # 생성부서(매장) 또는 생성매장의 branch_manager
        conditions = [model.owned_by_dept == user.department_id]

        # 일반 이용자
        if user.sys_id == "HO":
            if user.parent_dept_cd:
                ##본부 하위 팀 부서 리소스
                parent_teams_query = db.query(UserEntity).filter(
                    UserEntity.parent_dept_cd == user.parent_dept_cd
                )
                department_ids = list({i.department_id for i in parent_teams_query})
                team_conditions = [model.owned_by_dept.in_(department_ids)]
                conditions.extend(team_conditions)
                erp_ids = [i.erp_id for i in parent_teams_query]
            else:
                dept_query = db.query(UserEntity).filter(
                    UserEntity.department_id == user.department_id
                )
                erp_ids = [i.erp_id for i in dept_query]

            # 해당 본사 팀이 관리하는 매장 리소스
            shops_query = (
                db.query(UserEntity.department_id)
                .filter(
                    UserEntity.branch_manager.in_(erp_ids),
                    UserEntity.branch_manager.isnot(None),
                )
                .filter()
                .distinct()
            )
            shop_codes = [i[0] for i in shops_query]
            branch_conditions = [model.owned_by_dept.in_(shop_codes)]
            conditions.extend(branch_conditions)

            res_cond = [or_(*conditions)]

        # 매장 이용자
        else:
            res_cond = conditions

    return res_cond
