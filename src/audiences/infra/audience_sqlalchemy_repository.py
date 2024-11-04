from datetime import datetime

from sqlalchemy import String, and_, desc, func, or_, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import Alias

from src.audiences.domain.audience import Audience
from src.audiences.domain.variable_table_mapping import VariableTableMapping
from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.infra.dto.audience_info import AudienceInfo
from src.audiences.infra.dto.filter_condition import FilterCondition
from src.audiences.infra.dto.linked_campaign import LinkedCampaign
from src.audiences.infra.dto.upload_conditon import UploadCondition
from src.audiences.infra.entity.audience_count_by_month_entity import (
    AudienceCountByMonthEntity,
)
from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
)
from src.audiences.infra.entity.audience_entity import AudienceEntity
from src.audiences.infra.entity.audience_predefined_variable_entity import (
    AudiencePredefVariableEntity,
)
from src.audiences.infra.entity.audience_queries_entity import AudienceQueriesEntity
from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.audiences.infra.entity.audience_upload_condition_entity import (
    AudienceUploadConditionsEntity,
)
from src.audiences.infra.entity.audience_variable_options_entity import (
    AudienceVariableOptionsEntity,
)
from src.audiences.infra.entity.customer_promotion_master_entity import (
    CustomerPromotionMasterEntity,
)
from src.audiences.infra.entity.customer_promotion_react_summary_entity import (
    CustomerPromotionReactSummaryEntity,
)
from src.audiences.infra.entity.primary_rep_product_entity import (
    PrimaryRepProductEntity,
)
from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
from src.audiences.infra.entity.strategy_theme_audience_entity import (
    StrategyThemeAudienceMappingEntity,
)
from src.audiences.infra.entity.variable_table_list import (
    CustomerInfoStatusEntity,
    CustomerProductPurchaseSummaryEntity,
    GaViewMasterEntity,
)
from src.audiences.infra.entity.variable_table_mapping_entity import (
    VariableTableMappingEntity,
)
from src.audiences.routes.dto.response.default_exclude_audience import (
    DefaultExcludeAudience,
)
from src.audiences.utils.query_builder import execute_query_compiler
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.common.enums.role import RoleEnum
from src.common.utils.data_converter import DataConverter
from src.common.utils.model_converter import ModelConverter
from src.common.utils.string_utils import is_convertible_to_int
from src.core.exceptions.exceptions import NotFoundException
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class AudienceSqlAlchemy:

    def get_audiences(
        self, user: User, db: Session, is_exclude: bool | None = None
    ) -> list[AudienceInfo]:
        user_entity = db.query(UserEntity).filter(UserEntity.user_id == user.user_id).first()
        if user_entity is None:
            raise NotFoundException(detail={"message": "사용자를 찾지 못했습니다."})

        if is_exclude:
            conditions = [AudienceEntity.is_exclude == is_exclude]
            audience_name_column = func.concat(
                "(", AudienceEntity.audience_id, ") ", AudienceEntity.audience_name
            ).label("audience_name")

        else:
            conditions = self._object_access_condition(
                db=db, user=user_entity, model=AudienceEntity
            )
            audience_name_column = AudienceEntity.audience_name

        subq = (
            db.query(
                AudienceCountByMonthEntity.audience_id,
                func.max(AudienceCountByMonthEntity.stnd_month).label("maxdate"),
            )
            .group_by(AudienceCountByMonthEntity.audience_id)
            .subquery()
        )

        subq_maxdate = (
            db.query(AudienceCountByMonthEntity)
            .join(
                subq,
                and_(
                    AudienceCountByMonthEntity.audience_id == subq.c.audience_id,
                    AudienceCountByMonthEntity.stnd_month == subq.c.maxdate,
                ),
            )
            .subquery()
        )

        audience_filtered = (
            db.query(
                AudienceEntity.audience_id,
                audience_name_column,
                AudienceEntity.audience_status_code,
                AudienceEntity.audience_status_name,
                AudienceEntity.target_strategy,
                AudienceEntity.is_exclude,
                AudienceEntity.user_exc_deletable,
                AudienceEntity.update_cycle,
                AudienceEntity.description,
                AudienceEntity.created_at,
                AudienceEntity.updated_at,
                AudienceEntity.owned_by_dept,
                subq_maxdate.c.audience_count,
                AudienceStatsEntity.audience_unit_price,
                PrimaryRepProductEntity.main_product_id,
                PrimaryRepProductEntity.main_product_name,
            )
            .join(
                subq_maxdate,
                AudienceEntity.audience_id == subq_maxdate.c.audience_id,
            )
            .join(
                AudienceStatsEntity,
                AudienceEntity.audience_id == AudienceStatsEntity.audience_id,
            )
            .outerjoin(
                PrimaryRepProductEntity,
                AudienceEntity.audience_id == PrimaryRepProductEntity.audience_id,
            )
            .filter(
                AudienceEntity.audience_status_code != AudienceStatus.notdisplay.value,
                *conditions,
            )
            .order_by(desc(AudienceEntity.created_at))
        )

        result = audience_filtered.all()

        # 결과를 Pydantic 모델로 변환
        audiences = AudienceInfo.from_query(result)
        return audiences

    def get_audience(self, audience_id: str, db: Session) -> AudienceEntity | None:
        return db.query(AudienceEntity).filter(AudienceEntity.audience_id == audience_id).first()

    def get_audience_by_name(self, audience_name: str, db: Session) -> AudienceEntity | None:

        return (
            db.query(AudienceEntity).filter(AudienceEntity.audience_name == audience_name).first()
        )

    def create_audience(self, audience_dict, conditions, db: Session):

        entity = AudienceEntity(**audience_dict)
        db.add(entity)

        # 시퀀스 넘버를 가져오기 위해 flush()를 호출
        db.flush()
        audience_id = entity.audience_id

        # #audience_filter_conditions
        conditions["audience_id"] = audience_id
        audience_queries_req = AudienceQueriesEntity(**conditions)
        db.add(audience_queries_req)

        db.flush()

        return audience_id

    def create_audience_by_upload(
        self,
        audience_dict,
        insert_to_uploaded_audiences,
        upload_check_list,
        db: Session,
    ):
        audiences_req = AudienceEntity(**audience_dict)
        db.add(audiences_req)

        # 시퀀스 넘버를 가져오기 위해 flush()를 호출
        db.flush()
        audience_id = audiences_req.audience_id

        insert_to_uploaded_audiences["audience_id"] = audience_id
        audience_upload_condition = AudienceUploadConditionsEntity(**insert_to_uploaded_audiences)
        db.add(audience_upload_condition)

        # audience_cust_mapping
        obj = [
            AudienceCustomerMappingEntity(
                cus_cd=item,  ##cus_cd
                audience_id=audience_id,
            )
            for item in upload_check_list
        ]

        db.bulk_save_objects(obj)

        db.flush()

        return audience_id

    def get_db_filter_conditions(self, audience_id: str, db: Session) -> list[FilterCondition]:

        data = (
            db.query(
                AudienceQueriesEntity.audience_id,
                AudienceEntity.audience_name,
                AudienceQueriesEntity.conditions,
                AudienceQueriesEntity.exclusion_condition,
                AudienceQueriesEntity.created_at,
                AudienceQueriesEntity.updated_at,
            )
            .join(
                AudienceEntity,
                AudienceQueriesEntity.audience_id == AudienceEntity.audience_id,
            )
            .filter(AudienceQueriesEntity.audience_id == audience_id)
            .all()
        )

        return [
            FilterCondition(
                audience_id=row.audience_id,
                audience_name=row.audience_name,
                conditions=row.conditions,
                exclusion_condition=row.exclusion_condition,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in data
        ]

    def save_audience_list(self, audience_id, query, db: Session):

        result = db.execute(query).fetchall()

        obj = [
            AudienceCustomerMappingEntity(cus_cd=item[0], audience_id=audience_id)
            for item in result
        ]

        db.bulk_save_objects(obj)

    def get_all_customer(self, db: Session):
        return db.query(func.distinct(CustomerInfoStatusEntity.cus_cd).label("cus_cd"))

    def get_tablename_by_variable_id(self, variable_id: str, db: Session) -> VariableTableMapping:

        entity = (
            db.query(VariableTableMappingEntity)
            .filter(VariableTableMappingEntity.variable_id == variable_id)
            .first()
        )

        if not entity:
            raise NotFoundException(detail={"message": "변수-테이블 매핑 정보를 찾지 못했습니다."})

        return ModelConverter.entity_to_model(entity, VariableTableMapping)

    def get_linked_campaign(self, audience_id: str, db: Session) -> list[LinkedCampaign]:

        results = (
            db.query(
                StrategyThemeAudienceMappingEntity.audience_id,
                CampaignEntity.campaign_status_code,
            )
            .join(
                StrategyThemesEntity,
                StrategyThemeAudienceMappingEntity.strategy_theme_id
                == StrategyThemesEntity.strategy_theme_id,
            )
            .join(
                CampaignEntity,
                StrategyThemesEntity.strategy_id == CampaignEntity.strategy_id,
            )
            .filter(StrategyThemeAudienceMappingEntity.audience_id == audience_id)
            .all()
        )

        linked_campaigns = [
            LinkedCampaign(audience_id=row[0], campaign_status_code=row[1]) for row in results
        ]
        return linked_campaigns

    def calculate_frequency(self, column, label):
        """
        구매횟수 select절 반환함수
        """
        label = label.replace("_freq", "")
        frequency = func.count(func.distinct(column)).label(label)
        return frequency

    def calculate_recency(self, column, label):
        """
        구매경과일 select절 반환함수
        """
        label = label.replace("_recency", "")
        today = datetime.now().date()
        recency = (func.date(today) - func.to_date(func.max(column), "YYYYMMDD")).label(label)
        return recency

    def calculate_pur_cycle(self, column, label):
        """
        구매주기 select절 반환함수
        """
        label = label.replace("_pur_cycle", "")
        pur_cycle = func.case(
            func.count(func.distinct(column)) >= 2,
            (
                func.to_date(func.max(column), "YYYYMMDD")
                - func.to_date(func.min(column), "YYYYMMDD")
            )
            / (func.count(func.distinct(column)) - 1),
        ).label(label)
        return pur_cycle

    def get_calculate_method_by_label_name(self, column, label):
        """
        sale_dt_array unnest 컬럼 라벨에 따라 select 반환함수를 적용
        """
        if "freq" in label:
            return self.calculate_frequency(column, label)
        elif "recency" in label:
            return self.calculate_recency(column, label)
        elif "pur_cycle" in label:
            return self.calculate_pur_cycle(column, label)
        else:
            return

    def get_agg_value_with_subquery(self, subquery):
        """
        get_calculate_method_by_label_name 함수를 모든 서브쿼리 컬럼에 대해 적용
        """
        agg_select_query_list = [
            self.get_calculate_method_by_label_name(column, column.key) for column in subquery.c
        ]
        return agg_select_query_list

    def get_subquery_without_groupby(self, select_query_list, variabletable, db: Session):

        return db.query(
            func.distinct(variabletable.cus_cd).label("cus_cd"), *select_query_list
        ).subquery()

    def get_subquery_with_groupby(self, select_query_list, variabletable, db: Session):

        print("select_query_list")
        print(select_query_list)
        select_compile = execute_query_compiler(select_query_list[0])

        ga_columns = [
            "ga_view_master.product_code",
            "ga_view_master.product_name",
            "ga_view_master.page_title",
            "ga_view_master.full_category_name_1",
            "ga_view_master.full_category_name_2",
            "ga_view_master.full_category_name_3",
        ]

        if any(keyword in str(select_compile) for keyword in ga_columns):
            return (
                db.query(variabletable.cus_cd, *select_query_list)
                .group_by(variabletable.cus_cd, *select_query_list)
                .subquery()
            )

        return (
            db.query(variabletable.cus_cd, *select_query_list)
            .group_by(variabletable.cus_cd)
            .subquery()
        )

    def get_subquery_method(self, table_obj):
        """
        테이블에 따라 서브쿼리 생성 시 groupby 적용 여부를 지정하는 함수
        """
        if table_obj in (
            CustomerProductPurchaseSummaryEntity,
            PurchaseAnalyticsMasterStyle,
            CustomerPromotionMasterEntity,
            CustomerPromotionReactSummaryEntity,
            GaViewMasterEntity,
        ):
            return self.get_subquery_with_groupby
        else:
            return self.get_subquery_without_groupby

    def get_subquery_with_select_query_list(
        self, table_obj, select_query_list, idx, db: Session
    ) -> Alias:
        """
        서브쿼리가 필요없는 변수에 대한 집계쿼리 반환
        """
        subquery_method = self.get_subquery_method(table_obj)
        subquery = subquery_method(select_query_list, table_obj, db)
        sub_alias = subquery.alias(f"t{idx}")

        return sub_alias

    def get_subquery_with_array_select_query_list(
        self, table_obj, array_select_query_list, idx, db: Session
    ):
        """
        서브쿼리가 필요한 변수에 대한 집계쿼리 반환
        """
        subquery = self.get_subquery_without_groupby(array_select_query_list, table_obj, db)
        # agg_subquery = get_agg_value_with_subquery(db, subquery)
        agg_select_query_list = self.get_agg_value_with_subquery(subquery)
        agg_subquery = self.get_subquery_with_groupby(agg_select_query_list, subquery.c, db)
        sub_alias = agg_subquery.alias(f"t{idx}")
        return sub_alias

    def update_expired_audience_status(self, audience_id: str, db: Session):

        update_statement = (
            update(AudienceEntity)
            .where(AudienceEntity.audience_id == audience_id)
            .values(audience_status_code="notdisplay", audience_status_name="미표시")
        )
        result = db.execute(update_statement)

        if result.rowcount == 0:
            raise ValueError("해당하는 타겟 오디언스가 존재하지 않습니다.")

    def delete_audience(self, audience_id: str, db: Session):

        # 타겟 오디언스
        db.query(AudienceEntity).filter(AudienceEntity.audience_id == audience_id).delete()

        # 상세정보
        db.query(AudienceStatsEntity).filter(
            AudienceStatsEntity.audience_id == audience_id
        ).delete()

        # 오디언스 생성 쿼리
        db.query(AudienceQueriesEntity).filter(
            AudienceQueriesEntity.audience_id == audience_id
        ).delete()

        # 오디언스 업로드 정보
        db.query(AudienceUploadConditionsEntity).filter(
            AudienceUploadConditionsEntity.audience_id == audience_id
        ).delete()

        # 타겟 오디언스 수
        db.query(AudienceCountByMonthEntity).filter(
            AudienceCountByMonthEntity.audience_id == audience_id
        ).delete()

        # 타겟 오디언스 주 구매 대표상품
        db.query(PrimaryRepProductEntity).filter(
            PrimaryRepProductEntity.audience_id == audience_id
        ).delete()

        # 타겟오디언스 고객 리스트
        db.query(AudienceCustomerMappingEntity).filter(
            AudienceCustomerMappingEntity.audience_id == audience_id
        ).delete()

        db.flush()

    def _object_access_condition(self, db: Session, user: UserEntity, model: AudienceEntity):
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
            if "HO" == user.sys_id:
                if user.parent_dept_cd:  # pyright: ignore [reportGeneralTypeIssues]
                    ##본부 하위 팀 부서 리소스
                    parent_teams_query = db.query(UserEntity).filter(
                        UserEntity.parent_dept_cd == user.parent_dept_cd
                    )
                    department_ids = list({i.department_id for i in parent_teams_query})
                    team_conditions = [model.owned_by_dept.in_(department_ids)]  # type: ignore
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
                branch_conditions = [model.owned_by_dept.in_(shop_codes)]  # type: ignore
                conditions.extend(branch_conditions)

                res_cond = [or_(*conditions)]

            # 매장 이용자
            else:
                res_cond = conditions

        return res_cond

    def get_audience_stats(self, audience_id, db: Session):

        return (
            db.query(
                AudienceEntity.audience_id,
                AudienceEntity.audience_name,
                AudienceEntity.audience_status_code,
                AudienceEntity.audience_status_name,
                AudienceEntity.create_type_code,
                AudienceEntity.description,
                AudienceEntity.created_at,
                AudienceEntity.created_by,  # 생성 유저
                UserEntity.username.label("created_by_name"),  # 생성 부서
                UserEntity.department_name.label("owned_by_dept_name"),  # 생성 부서 abb명
                UserEntity.department_abb_name.label("owned_by_dept_abb_name"),  # 생성 부서 abb명
                AudienceStatsEntity.audience_count,
                AudienceStatsEntity.audience_count_gap,
                AudienceStatsEntity.net_audience_count,
                AudienceStatsEntity.agg_period_start,
                AudienceStatsEntity.agg_period_end,
                AudienceStatsEntity.excluded_customer_count,
                AudienceStatsEntity.audience_portion,
                AudienceStatsEntity.audience_portion_gap,
                AudienceStatsEntity.audience_unit_price,
                AudienceStatsEntity.audience_unit_price_gap,
                AudienceStatsEntity.revenue_per_audience,
                AudienceStatsEntity.purchase_per_audience,
                AudienceStatsEntity.revenue_per_purchase,
                AudienceStatsEntity.avg_pur_item_count,
                AudienceStatsEntity.retention_rate_3m,
                AudienceStatsEntity.response_rate,
                AudienceStatsEntity.stat_updated_at,
            )
            .outerjoin(
                AudienceStatsEntity,
                AudienceEntity.audience_id == AudienceStatsEntity.audience_id,
            )
            .outerjoin(
                UserEntity,
                AudienceEntity.created_by == func.cast(UserEntity.user_id, String),
            )
            .filter(AudienceEntity.audience_id == audience_id)
        )

    def get_audience_products(self, audience_id, db: Session):

        return db.query(PrimaryRepProductEntity).filter(
            PrimaryRepProductEntity.audience_id == audience_id
        )

    def get_audience_count(self, audience_id, db: Session):

        return db.query(AudienceCountByMonthEntity).filter(
            AudienceCountByMonthEntity.audience_id == audience_id
        )

    def get_variables_options(self, access_lv, db: Session):

        data = (
            db.query(
                AudienceVariableOptionsEntity.option_seq,
                AudienceVariableOptionsEntity.predef_var_seq,
                AudiencePredefVariableEntity.variable_id,
                AudiencePredefVariableEntity.variable_name,
                AudiencePredefVariableEntity.variable_group_code,
                AudiencePredefVariableEntity.variable_group_name,
                AudiencePredefVariableEntity.combination_type,
                AudiencePredefVariableEntity.additional_variable,
                AudienceVariableOptionsEntity.option_id,
                AudienceVariableOptionsEntity.option_name,
                AudienceVariableOptionsEntity.data_type,
                AudienceVariableOptionsEntity.data_type_desc,
                AudienceVariableOptionsEntity.cell_type,
                AudienceVariableOptionsEntity.component_order_cols,
                AudiencePredefVariableEntity.input_cell_type,
            )
            .outerjoin(
                AudienceVariableOptionsEntity,
                AudiencePredefVariableEntity.variable_id
                == AudienceVariableOptionsEntity.variable_id,
            )
            .filter(AudiencePredefVariableEntity.access_level >= access_lv)
        )

        return DataConverter.convert_query_to_df(data)

    def get_options(self, db: Session):

        return (
            db.query(
                AudienceVariableOptionsEntity.option_id,
                AudienceVariableOptionsEntity.option_name,
                AudienceVariableOptionsEntity.data_type,
                AudienceVariableOptionsEntity.input_cell_type,
                AudienceVariableOptionsEntity.option_order_cols,
            )
            .join(
                AudiencePredefVariableEntity,
                AudienceVariableOptionsEntity.variable_id
                == AudiencePredefVariableEntity.variable_id,
            )
            .order_by(AudienceVariableOptionsEntity.option_order_cols)
            .distinct()
        )

    def get_audience_cust_with_audience_id(self, audience_id, db: Session):

        return db.query(AudienceCustomerMappingEntity.cus_cd).filter(
            AudienceCustomerMappingEntity.audience_id == audience_id
        )

    def get_audience_detail(self, audience_id, db: Session) -> Audience:

        entity = db.query(AudienceEntity).filter(AudienceEntity.audience_id == audience_id).first()

        if not entity:
            raise NotFoundException(detail={"message": "타겟 오디언스를 찾지 못했습니다."})

        return ModelConverter.entity_to_model(entity, Audience)

    def get_audience_upload_info(self, audience_id, db: Session) -> list[UploadCondition]:

        data = (
            db.query(
                AudienceEntity.audience_name,
                AudienceUploadConditionsEntity.audience_id,
                AudienceUploadConditionsEntity.template_type,
                AudienceUploadConditionsEntity.upload_count,
                AudienceUploadConditionsEntity.checked_count,
                AudienceUploadConditionsEntity.checked_list,
                AudienceUploadConditionsEntity.created_at,
                AudienceUploadConditionsEntity.updated_at,
            )
            .join(
                AudienceEntity,
                AudienceUploadConditionsEntity.audience_id == AudienceEntity.audience_id,
            )
            .filter(AudienceUploadConditionsEntity.audience_id == audience_id)
            .all()
        )

        upload_conditions = [
            UploadCondition(
                audience_name=row.audience_name,
                audience_id=row.audience_id,
                template_type=row.template_type,
                upload_count=row.upload_count,
                checked_count=row.checked_count,
                create_type_code=AudienceCreateType.Upload.value,
                create_type_name=AudienceCreateType.Upload.description,
                checked_list=row.checked_list,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in data
        ]

        return upload_conditions

    def get_actual_list_from_csv(self, uploaded_rows, target_column, entity, db: Session) -> list:

        selected_column = getattr(entity, target_column)

        res = [db.query(func.distinct(selected_column).filter(selected_column.in_(uploaded_rows)))]

        if entity == CsvTemplates.shop_cd.source:
            res.append(
                db.query(func.distinct(CsvTemplates.cus_cd.source.cus_cd)).filter(
                    CsvTemplates.cus_cd.source.main_shop.in_(uploaded_rows)
                )
            )

        return res

    def update_cycle(self, audience_id: str, update_cycle: str, db: Session):

        update_statement = (
            update(AudienceEntity)
            .where(AudienceEntity.audience_id == audience_id)
            .values(update_cycle=update_cycle)
        )
        result = db.execute(update_statement)

        if result.rowcount == 0:
            raise NotFoundException(detail={"message": "타겟 오디언스를 찾지 못했습니다."})

        db.flush()

    def delete_audience_info_for_update(self, audience_id, db: Session):
        """
        타겟오디언스 생성 조건 수정 후 기존 데이터 삭제 함수
        """
        # 타겟 오디언스 고객 리스트
        db.query(AudienceCustomerMappingEntity).filter(
            AudienceCustomerMappingEntity.audience_id == audience_id
        ).delete()
        # 상세정보
        db.query(AudienceStatsEntity).filter(
            AudienceStatsEntity.audience_id == audience_id
        ).delete()

        # 타겟 오디언스 수
        db.query(AudienceCountByMonthEntity).filter(
            AudienceCountByMonthEntity.stnd_month == func.to_char(func.current_date(), "YYYYMM"),
            AudienceCountByMonthEntity.audience_id == audience_id,
        ).delete()

        # 타겟 오디언스 주 구매 대표상품
        db.query(PrimaryRepProductEntity).filter(
            PrimaryRepProductEntity.audience_id == audience_id
        ).delete()

        # 오디언스 CSV 삭제
        db.query(AudienceUploadConditionsEntity).filter(
            AudienceUploadConditionsEntity.audience_id == audience_id
        ).delete()

        # 오디언스 생성 쿼리 삭제
        db.query(AudienceQueriesEntity).filter(
            AudienceQueriesEntity.audience_id == audience_id
        ).delete()

        db.flush()

    def update_by_upload(
        self,
        filter_audience,
        insert_to_uploaded_audiences,
        insert_to_audiences,
        checked_list,
        db: Session,
    ):

        audience_id = filter_audience["audience_id"]

        update_statement = (
            update(AudienceEntity)
            .where(AudienceEntity.audience_id == audience_id)
            .values(insert_to_audiences)
        )
        update_result = db.execute(update_statement)

        if update_result.rowcount == 0:
            raise ValueError("해당 타겟 오디언스를 찾지 못했습니다.")

        db.add(AudienceUploadConditionsEntity(**insert_to_uploaded_audiences))

        # audience_cust_mapping
        obj = [
            AudienceCustomerMappingEntity(
                cus_cd=item,
                audience_id=audience_id,
            )
            for item in checked_list
        ]

        db.bulk_save_objects(obj)

        db.flush()

    def update_by_filter(
        self, audience_id, insert_to_filter_conditions, insert_to_audiences, db: Session
    ):
        update_statement = (
            update(AudienceEntity)
            .where(AudienceEntity.audience_id == audience_id)
            .values(insert_to_audiences)
        )
        update_result = db.execute(update_statement)
        print("audience_update_entity")
        print(update_result)

        if update_result.rowcount == 0:
            raise ValueError("해당 타겟 오디언스를 찾지 못했습니다.")

        audience_query = (
            db.query(AudienceQueriesEntity)
            .filter(AudienceQueriesEntity.audience_id == audience_id)
            .first()
        )

        if audience_query:
            query_update_statement = (
                update(AudienceQueriesEntity)
                .where(AudienceQueriesEntity.audience_id == audience_id)
                .values(insert_to_filter_conditions)
            )
            query_update_result = db.execute(query_update_statement)

            if query_update_result.rowcount == 0:
                raise ValueError("해당 타겟 오디언스를 찾지 못했습니다.")
        else:
            insert_to_filter_conditions["audience_id"] = audience_id
            db.add(AudienceQueriesEntity(**insert_to_filter_conditions))

        db.flush()

    def get_audiences_ids_by_strategy_id(
        self, strategy_id: str, db: Session, strategy_theme_id: str | None = None
    ) -> list[str]:

        base_query = (
            db.query(StrategyThemeAudienceMappingEntity.audience_id)
            .join(
                StrategyThemesEntity,
                StrategyThemeAudienceMappingEntity.strategy_theme_id
                == StrategyThemesEntity.strategy_theme_id,
            )
            .filter(StrategyThemesEntity.strategy_id == strategy_id)
        )

        if strategy_theme_id:
            base_query = base_query.filter(
                StrategyThemesEntity.strategy_theme_id == strategy_theme_id
            )

        audience_ids = base_query.all()

        audience_ids = [aud[0] for aud in audience_ids]
        return audience_ids

    def get_audiences_by_condition(
        self, audience_ids, search_keyword, is_exclude, db: Session
    ) -> list[IdWithLabel]:

        conditions = []
        if is_exclude:
            conditions.append(AudienceEntity.is_exclude == is_exclude)
        if search_keyword:
            modified_string = search_keyword.replace("aud-", "")
            keyword = f"%{search_keyword}%"

            if is_convertible_to_int(modified_string):
                conditions.append(AudienceEntity.audience_id.ilike(keyword))  # audience_id
            else:
                conditions.append(AudienceEntity.audience_name.ilike(keyword))  # audience_name

        result = (
            db.query(
                AudienceEntity.audience_id.label("id"),
                AudienceEntity.audience_name.label("name"),
            )
            .filter(
                AudienceEntity.is_exclude.is_(False),
                AudienceEntity.audience_id.in_(audience_ids),
                AudienceEntity.audience_status_code
                != AudienceStatus.notdisplay.value,  # 캠페인 연결된 적 있는 삭제 오브젝트 제외
                *conditions,
            )
            .all()
        )

        return [
            IdWithLabel(
                id=data.id,
                name=data.name,
                label=self._create_label(data),
            )
            for data in result
        ]

    def get_audiences_by_condition_without_strategy_id(
        self,
        search_keyword,
        is_exclude,
        db: Session,
        target_strategy: str | None = None,
    ) -> list[IdWithLabel]:

        conditions = [AudienceEntity.is_exclude == is_exclude]

        if search_keyword:
            modified_string = search_keyword.replace("aud-", "")
            keyword = f"%{search_keyword}%"

            if is_convertible_to_int(modified_string):
                conditions.append(AudienceEntity.audience_id.ilike(keyword))  # audience_id
            else:
                conditions.append(AudienceEntity.audience_name.ilike(keyword))  # audience_name

        strategy_conditions = [
            AudienceEntity.audience_status_code != AudienceStatus.notdisplay.value
        ]

        if target_strategy and target_strategy != "custom":
            strategy_conditions.append(AudienceEntity.target_strategy == target_strategy)

        result = (
            db.query(
                AudienceEntity.audience_id.label("id"),
                AudienceEntity.audience_name.label("name"),
            )
            .filter(
                *conditions,
                *strategy_conditions,
            )
            .all()
        )

        return [
            IdWithLabel(
                id=data.id,
                name=data.name,
                label=self._create_label(data),
            )
            for data in result
        ]

    def _create_label(self, data):
        return f"({data.id}) {data.name}"

    def get_default_exclude(self, user, db: Session) -> list[DefaultExcludeAudience]:

        base_query = db.query(
            AudienceEntity.audience_id,
            AudienceEntity.audience_name,
            AudienceEntity.user_exc_deletable,
        )
        if user.role_id == "branch_user":
            entities = base_query.filter(
                or_(
                    and_(
                        AudienceEntity.is_exclude.is_(True),
                        AudienceEntity.default_excl_on_camp.is_(True),
                        AudienceEntity.audience_id != "aud-000459",  ## branch_user를 위한 예외로직
                    ),
                    AudienceEntity.audience_id == "aud-000461",  ## branch_user를 위한 예외로직
                ),
            ).all()
        else:
            entities = base_query.filter(
                AudienceEntity.is_exclude.is_(True),
                AudienceEntity.default_excl_on_camp.is_(True),
            ).all()

        return [
            DefaultExcludeAudience(
                id=entity.audience_id,
                name=entity.audience_name,
                user_exc_deletable=entity.user_exc_deletable,
            )
            for entity in entities
        ]

    def update_exclude_status(self, audience_id, is_exclude, db: Session):
        update_statement = (
            update(AudienceEntity)
            .where(AudienceEntity.audience_id == audience_id)
            .values(is_exclude=is_exclude, user_exc_deletable=True)
        )
        result = db.execute(update_statement)

        db.commit()

        if result.rowcount == 0:
            raise ValueError("해당하는 타겟 오디언스가 존재하지 않습니다.")

    def get_linked_strategy(self, audience_id, db: Session) -> list:

        strategy_theme_audience = (
            db.query(StrategyThemeAudienceMappingEntity)
            .filter(StrategyThemeAudienceMappingEntity.audience_id == audience_id)
            .first()
        )

        if not strategy_theme_audience:
            return []

        strategy_id_entities = (
            db.query(StrategyEntity.strategy_id)
            .join(
                StrategyThemesEntity, StrategyThemesEntity.strategy_id == StrategyEntity.strategy_id
            )
            .filter(
                StrategyThemesEntity.strategy_theme_id == strategy_theme_audience.strategy_theme_id,
                ~StrategyEntity.is_deleted,
            )
        )

        return [strategy.strategy_id for strategy in strategy_id_entities]
