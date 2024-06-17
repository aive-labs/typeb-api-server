from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import or_, update
from sqlalchemy.orm import Session

from src.contents.domain.contents import Contents
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

    def get_contents_url_list(self):
        with self.db() as db:
            entities = db.query(ContentsEntity).all()
            return [entity.contents_url for entity in entities]

    def get_contents_list(
        self, based_on, sort_by, contents_status=None, query=None
    ) -> list[ContentsResponse]:
        with self.db() as db:
            sort_col = getattr(ContentsEntity, based_on)
            # get all contents_data
            base_query = (
                db.query(
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
                )
                .join(ContentsEntity, ContentsMenuEntity.code == ContentsEntity.subject)
                .filter(~ContentsEntity.is_deleted)
            )

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
                ContentsResponse(
                    contents_id=entity.contents_id,
                    contents_name=entity.contents_name,
                    contents_status=entity.contents_status,
                    contents_body=entity.contents_body,
                    plain_text=entity.plain_text,
                    sty_cd=entity.sty_cd,
                    subject=entity.subject,
                    subject_name=entity.subject_name,
                    material1=entity.material1,
                    material2=entity.material2,
                    template=entity.template,
                    additional_prompt=entity.additional_prompt,
                    thumbnail_uri=entity.thumbnail_uri,
                    contents_url=entity.contents_url,
                    publication_start=entity.publication_start,
                    publication_end=entity.publication_end,
                    contents_tags=entity.contents_tags,
                    created_by=entity.created_by,
                    created_at=entity.created_at,
                    updated_by=entity.updated_by,
                    updated_at=entity.updated_at,
                )
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

    def get_contents_detail(self, contents_id):
        with self.db() as db:
            entity = (
                db.query(ContentsEntity)
                .filter(
                    ContentsEntity.contents_id == contents_id,
                    ~ContentsEntity.is_deleted,
                )
                .first()
            )

            if not entity:
                raise NotFoundError("해당하는 콘텐츠가 존재하지 않습니다.")

            return ModelConverter.entity_to_model(entity, Contents)

    def delete_contents(self, contents_id):
        with self.db() as db:
            update_statement = (
                update(ContentsEntity)
                .where(ContentsEntity.contents_id == contents_id)
                .values(is_deleted=True)
            )

            db.execute(update_statement)
            db.commit()
