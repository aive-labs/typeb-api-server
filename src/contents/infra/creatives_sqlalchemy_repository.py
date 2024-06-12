from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import case, func, or_, update
from sqlalchemy.orm import Session

from src.contents.domain.creatives import Creatives
from src.contents.infra.entity.creatives_entity import CreativesEntity
from src.contents.infra.entity.style_master_entity import StyleMaster
from src.contents.routes.dto.request.contents_create import StyleObjectBase
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.core.exceptions import NotFoundError
from src.utils.file.model_converter import ModelConverter


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

    def find_by_id(self, id: int) -> Creatives:
        with self.db() as db:
            entity = (
                db.query(CreativesEntity)
                .filter(CreativesEntity.creative_id == id, ~CreativesEntity.is_deleted)
                .first()
            )

            if entity is None:
                raise NotFoundError("Not found CreativesEntity")

            return ModelConverter.entity_to_model(entity, Creatives)

    def get_all_creatives(self, based_on, sort_by, asset_type=None, query=None):
        with self.db() as db:
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
                    StyleMaster.sty_nm,
                    StyleMaster.sty_cd,
                    StyleMaster.rep_nm,
                    case(  # pyright: ignore [reportCallIssue]
                        (  # pyright: ignore [reportArgumentType]
                            StyleMaster.year2 is not None,
                            func.concat(
                                StyleMaster.year2, "(", StyleMaster.sty_season_nm, ")"
                            ),
                        ),
                        else_=None,
                    ).label("year_season"),
                    StyleMaster.it_gb_nm,
                    StyleMaster.item_nm,
                    StyleMaster.item_sb_nm,
                    StyleMaster.purpose1.label("purpose"),
                    StyleMaster.cons_pri.label("price"),
                    CreativesEntity.creative_tags.label("creative_tags"),
                    CreativesEntity.updated_by.label("updated_by"),
                    CreativesEntity.updated_at.label("updated_at"),
                )
                .outerjoin(StyleMaster, StyleMaster.sty_cd == CreativesEntity.style_cd)
                .filter(~CreativesEntity.is_deleted)
            )

            if sort_by == "desc":
                sort_col = sort_col.desc()
            else:
                sort_col = sort_col.asc()
            base_query = base_query.order_by(sort_col)

            if asset_type:
                base_query = base_query.filter(
                    CreativesEntity.image_asset_type == asset_type.value
                )

            if query:
                query = f"%{query}%"
                # check query in sty_nm, tags, image_name
                base_query = base_query.filter(
                    or_(
                        StyleMaster.sty_nm.ilike(query),
                        StyleMaster.sty_cd.ilike(query),
                        CreativesEntity.creative_tags.ilike(query),
                        CreativesEntity.image_uri.ilike(query),
                    )
                )

            return [CreativeBase.model_validate(item) for item in base_query.all()]

    def get_simple_style_list(self) -> list[StyleObjectBase]:
        with self.db() as db:
            style_masters = db.query(
                StyleMaster.sty_cd.label("style_cd"),
                func.concat(
                    "(", StyleMaster.sty_cd, ")", " ", StyleMaster.sty_nm
                ).label("style_object_name"),
            ).all()

            return [
                StyleObjectBase(
                    style_cd=item.style_cd, style_object_name=item.style_object_name
                )
                for item in style_masters
            ]

    def update(self, creative_id, creative_update_dict) -> Creatives:
        with self.db() as db:
            creative_data = (
                db.query(CreativesEntity)
                .filter(
                    CreativesEntity.creative_id == creative_id,
                    ~CreativesEntity.is_deleted,
                )
                .first()
            )

            if creative_data is None:
                raise NotFoundError("Creative가 존재하지 않습니다")

            update_statement = (
                update(CreativesEntity)
                .where(CreativesEntity.creative_id == creative_id)
                .values(update_values=creative_update_dict)
            )

            db.execute(update_statement)
            db.commit()

            return ModelConverter.entity_to_model(creative_data, Creatives)

    def save_creatives(self, creatives_list):
        with self.db() as db:
            entities = [
                CreativesEntity.from_model(creatives) for creatives in creatives_list
            ]
            db.add_all(entities)
            db.commit()

    def delete(self, creative_id):
        with self.db() as db:
            update_statement = (
                update(CreativesEntity)
                .where(CreativesEntity.creative_id == creative_id)
                .values(is_deleted=True)
            )

            db.execute(update_statement)
            db.commit()
