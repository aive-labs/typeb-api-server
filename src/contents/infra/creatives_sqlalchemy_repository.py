from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import case, func, or_, update
from sqlalchemy.orm import Session

from src.common.utils.model_converter import ModelConverter
from src.contents.domain.creatives import Creatives
from src.contents.infra.dto.response.creative_recommend import CreativeRecommend
from src.contents.infra.entity.creatives_entity import CreativesEntity
from src.contents.infra.entity.style_master_entity import StyleMasterEntity
from src.contents.routes.dto.request.contents_create import StyleObject
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.core.exceptions.exceptions import NotFoundException


class CreativesSqlAlchemy:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def find_by_id(self, id: int, db: Session) -> Creatives:

        entity = (
            db.query(CreativesEntity)
            .filter(CreativesEntity.creative_id == id, ~CreativesEntity.is_deleted)
            .first()
        )

        if entity is None:
            raise NotFoundException(detail={"message": "소재를 찾지 못했습니다."})

        return ModelConverter.entity_to_model(entity, Creatives)

    def get_all_creatives(self, based_on, sort_by, db: Session, asset_type=None, query=None):
        """소재 목록을 조회하는 함수, style_master와 left 조인하여 데이터 조회
        # add based_on, sort_by options
        """
        sort_col = getattr(CreativesEntity, based_on)

        base_query = (
            db.query(
                CreativesEntity.creative_id,
                CreativesEntity.image_asset_type,
                CreativesEntity.image_uri,
                CreativesEntity.image_path,
                CreativesEntity.image_source,
                StyleMasterEntity.sty_nm,
                StyleMasterEntity.sty_cd,
                StyleMasterEntity.rep_nm,
                case(
                    (
                        StyleMasterEntity.year2.isnot(None),
                        func.concat(
                            StyleMasterEntity.year2,
                            "(",
                            StyleMasterEntity.sty_season_nm,
                            ")",
                        ),
                    ),
                    else_=None,
                ).label("year_season"),
                StyleMasterEntity.it_gb_nm,
                StyleMasterEntity.item_nm,
                StyleMasterEntity.item_sb_nm,
                StyleMasterEntity.purpose1.label("purpose"),
                StyleMasterEntity.cons_pri.label("price"),
                CreativesEntity.creative_tags.label("creative_tags"),
                CreativesEntity.updated_by.label("updated_by"),
                CreativesEntity.updated_at.label("updated_at"),
            )
            .outerjoin(
                StyleMasterEntity,
                StyleMasterEntity.sty_cd == CreativesEntity.style_cd,
            )
            .filter(~CreativesEntity.is_deleted)
        )

        if sort_by == "desc":
            sort_col = sort_col.desc()
        else:
            sort_col = sort_col.asc()
        base_query = base_query.order_by(sort_col)

        if asset_type:
            base_query = base_query.filter(CreativesEntity.image_asset_type == asset_type.value)

        if query:
            query = f"%{query}%"
            # check query in sty_nm, tags, image_name
            base_query = base_query.filter(
                or_(
                    StyleMasterEntity.sty_nm.ilike(query),
                    StyleMasterEntity.sty_cd.ilike(query),
                    CreativesEntity.creative_tags.ilike(query),
                    CreativesEntity.image_uri.ilike(query),
                )
            )

        return [CreativeBase.model_validate(item) for item in base_query.all()]

    def get_simple_style_list(self, db: Session) -> list[StyleObject]:

        style_masters = db.query(
            StyleMasterEntity.sty_cd.label("style_cd"),
            func.concat("(", StyleMasterEntity.sty_cd, ")", " ", StyleMasterEntity.sty_nm).label(
                "style_object_name"
            ),
        ).all()

        return [
            StyleObject(style_cd=item.style_cd, style_object_name=item.style_object_name)
            for item in style_masters
        ]

    def update(self, creative_id, creative_update_dict, db: Session) -> Creatives:

        creative_data = (
            db.query(CreativesEntity)
            .filter(
                CreativesEntity.creative_id == creative_id,
                ~CreativesEntity.is_deleted,
            )
            .first()
        )

        if creative_data is None:
            raise NotFoundException(detail={"message": "Creative가 존재하지 않습니다"})

        update_statement = (
            update(CreativesEntity)
            .where(CreativesEntity.creative_id == creative_id)
            .values(creative_update_dict)
        )

        db.execute(update_statement)

        return ModelConverter.entity_to_model(creative_data, Creatives)

    def save_creatives(self, creatives_list, db: Session):

        entities = [CreativesEntity.from_model(creatives) for creatives in creatives_list]
        db.add_all(entities)

    def delete(self, creative_id, db: Session):

        update_statement = (
            update(CreativesEntity)
            .where(CreativesEntity.creative_id == creative_id)
            .values(is_deleted=True)
        )

        db.execute(update_statement)

    def get_creatives_for_contents(
        self, style_cd_list, given_tag, tag_nm, limit, db: Session
    ) -> list[CreativeRecommend]:

        filter_conditions = []

        if tag_nm != "":
            filter_conditions.append(CreativesEntity.creative_tags.ilike(f"%{tag_nm}%"))
            filter_conditions.append(CreativesEntity.style_object_name.ilike(f"%{tag_nm}%"))
        elif len(style_cd_list) > 0:
            filter_conditions.append(func.lower(CreativesEntity.style_cd).in_(style_cd_list))

        filter_conditions.append(~CreativesEntity.is_deleted)

        query = db.query(CreativesEntity).filter(or_(*filter_conditions))

        if style_cd_list:
            query = self._add_style_order(query, style_cd_list)

        if given_tag:
            query = self._add_tag_order(given_tag, query)

        # query = self._add_file_order(query)

        result = query.limit(limit).all()

        return [ModelConverter.entity_to_model(entity, CreativeRecommend) for entity in result]

    # def _add_file_order(self, query):
    #
    #     # TODO
    #     file_order = case(
    #         (or_(
    #             func.lower(CreativesEntity.image_uri).endswith("1.jpg"),
    #             func.lower(CreativesEntity.image_uri).endswith("1.png")),
    #          0),
    #         else_=1,
    #     )
    #     query = query.order_by(file_order)
    #     return query

    def _add_tag_order(self, given_tag, query):
        tag_order = (
            func.array_position(func.string_to_array(CreativesEntity.creative_tags, ","), given_tag)
            .desc()
            .nullslast()
        )
        query = query.order_by(tag_order)
        return query

    def _add_style_order(self, query, style_cd_list):
        code_order = case(
            {code: index for index, code in enumerate(style_cd_list)},
            value=CreativesEntity.style_cd,
            else_=len(style_cd_list),
        )
        query = query.order_by(code_order)
        return query

    def get_creatives_by_style_cd(self, style_cd, db) -> list[CreativeBase]:
        entities: list[CreativesEntity] = (
            db.query(CreativesEntity)
            .filter(~CreativesEntity.is_deleted, CreativesEntity.style_cd == style_cd)
            .all()
        )
        creative_base_list = [
            CreativeBase(
                sty_nm=entity.style_object_name,
                sty_cd=entity.style_cd,
                creative_id=entity.creative_id,
                image_asset_type=entity.image_asset_type,
                image_source=entity.image_source,
                image_uri=entity.image_uri,
                image_path=entity.image_path,
                creative_tags=entity.creative_tags,
            )
            for entity in entities
        ]

        return creative_base_list

    def get_creative_by_id(self, creative_id, db) -> Creatives:
        creative_data = (
            db.query(CreativesEntity)
            .filter(
                CreativesEntity.creative_id == creative_id,
                ~CreativesEntity.is_deleted,
            )
            .first()
        )

        if creative_data is None:
            raise NotFoundException(detail={"message": "Creative가 존재하지 않습니다"})

        return ModelConverter.entity_to_model(creative_data, Creatives)
