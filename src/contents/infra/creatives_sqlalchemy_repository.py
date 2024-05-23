from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from src.contents.infra.entity.creatives_entity import Creatives
from src.contents.infra.entity.style_master_entity import StyleMaster


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

    def get_all_creatives(self, based_on, sort_by, asset_type=None, query=None):
        with self.db() as db:
            """소재 목록을 조회하는 함수, style_master와 left 조인하여 데이터 조회
            # add based_on, sort_by options
            """
            sort_col = getattr(Creatives, based_on)

            base_query = db.query(
                Creatives.creative_id,
                Creatives.image_asset_type,
                Creatives.image_uri,
                Creatives.image_path,
                StyleMaster.sty_nm,
                StyleMaster.sty_cd,
                StyleMaster.rep_nm,
                case(
                    (
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
                Creatives.creative_tags.label("creative_tags"),
                Creatives.updated_by.label("updated_by"),
                Creatives.updated_at.label("updated_at"),
            ).outerjoin(StyleMaster, StyleMaster.sty_cd == Creatives.style_cd)

            if sort_by == "desc":
                sort_col = sort_col.desc()
            else:
                sort_col = sort_col.asc()
            base_query = base_query.order_by(sort_col)

            if asset_type:
                base_query = base_query.filter(
                    Creatives.image_asset_type == asset_type.value
                )
            if query:
                query = f"%{query}%"
                # check query in sty_nm, tags, image_name
                base_query = base_query.filter(
                    or_(
                        StyleMaster.sty_nm.ilike(query),
                        StyleMaster.sty_cd.ilike(query),
                        Creatives.creative_tags.ilike(query),
                        Creatives.image_uri.ilike(query),
                    )
                )
            return base_query.all()
