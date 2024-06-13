from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.infra.entity.contents_entity import ContentsEntity
from src.contents.infra.entity.contents_menu_entity import ContentsMenuEntity
from src.core.exceptions import NotFoundError
from src.utils.file.model_converter import ModelConverter


class ContentsSqlAlchemy:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def add_contents(self, contents: ContentsEntity):
        with self.db() as db:
            db.add(contents)
            db.commit()

    def get_subject(self, style_yn) -> list[ContentsMenu]:
        style_yn = "y" if style_yn else "n"
        with self.db() as db:
            entities = (
                db.query(ContentsMenuEntity)
                .filter(
                    ContentsMenuEntity.menu_type == "subject",
                    ContentsMenuEntity.style_yn == style_yn,
                )
                .order_by(ContentsMenuEntity.code)
                .all()
            )

            return [
                ModelConverter.entity_to_model(entity, ContentsMenu)
                for entity in entities
            ]

    def get_menu_map(self, code) -> list[ContentsMenu]:
        with self.db() as db:
            entity = (
                db.query(ContentsMenuEntity)
                .filter(ContentsMenuEntity.code == code)
                .first()
            )
            if not entity:
                raise NotFoundError("해당 메뉴를 찾지 못했습니다.")

            subject_style_yn = entity.style_yn

            subject = f"%{code}%"

            entities = (
                db.query(ContentsMenuEntity)
                .filter(ContentsMenuEntity.subject_with.ilike(subject))
                .filter(ContentsMenuEntity.style_yn == subject_style_yn)
                .order_by(ContentsMenuEntity.code)
                .all()
            )

            return [
                ModelConverter.entity_to_model(entity, ContentsMenu)
                for entity in entities
            ]

    def get_contents_list(
        self, based_on, sort_by, contents_status=None, query=None
    ) -> list[ContentsResponse]:
        with self.db() as db:
            sort_col = getattr(ContentsEntity, based_on)
            # get all contents_data
            base_query = db.query(
                ContentsEntity.contents_id,
                ContentsEntity.contents_name,
                ContentsEntity.contents_status,
                ContentsEntity.contents_body,
                ContentsEntity.plain_text,
                ContentsEntity.sty_cd,
                ContentsEntity.subject,
                ContentsMenuEntity.name.label("subject_name"),
                ContentsEntity.material1,
                ContentsEntity.material2,
                ContentsEntity.template,
                ContentsEntity.thumbnail_uri,
                ContentsEntity.contents_url,
                ContentsEntity.publication_start,
                ContentsEntity.publication_end,
                ContentsEntity.additional_prompt,
                ContentsEntity.contents_tags,
                ContentsEntity.created_by,
                ContentsEntity.created_at,
                ContentsEntity.updated_by,
                ContentsEntity.updated_at,
            ).join(ContentsEntity, ContentsMenuEntity.code == ContentsEntity.subject)

            if sort_by == "desc":
                sort_col = sort_col.desc()
            else:
                sort_col = sort_col.asc()
            base_query = base_query.order_by(sort_col)

            if contents_status:
                base_query = base_query.filter(
                    ContentsEntity.contents_status == contents_status
                )
            if query:
                query = f"%{query}%"
                # check query in sty_nm, tags, image_name
                base_query = base_query.filter(
                    or_(
                        ContentsEntity.contents_name.ilike(query),
                        ContentsEntity.contents_tags.ilike(query),
                    )
                )
            entities = base_query.all()
            return [
                ModelConverter.entity_to_model(entity, ContentsResponse)
                for entity in entities
            ]

    def get_subject_by_code(self, subject) -> ContentsMenu:
        with self.db() as db:
            entity = (
                db.query(ContentsMenuEntity)
                .filter(ContentsMenuEntity.code == subject)
                .first()
            )

            if not entity:
                raise NotFoundError("해당하는 menu가 존재하지 않습니다.")

            return ModelConverter.entity_to_model(entity, ContentsMenu)
