from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import or_, update
from sqlalchemy.orm import Session

from src.common.utils.model_converter import ModelConverter
from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.infra.entity.contents_entity import ContentsEntity
from src.contents.infra.entity.contents_menu_entity import ContentsMenuEntity
from src.core.exceptions.exceptions import NotFoundException
from src.search.routes.dto.id_with_item_response import IdWithItem
from src.strategy.enums.recommend_model import RecommendModels


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

    def add_contents(self, contents: ContentsEntity, db: Session) -> ContentsResponse:

        db.add(contents)

        return ModelConverter.entity_to_model(contents, ContentsResponse)

    def get_subject(self, style_yn, db: Session) -> list[ContentsMenu]:
        style_yn = "y" if style_yn else "n"
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
            ModelConverter.entity_to_model(entity, ContentsMenu) for entity in entities
        ]

    def get_menu_map(self, code, db: Session) -> list[ContentsMenu]:

        entity = (
            db.query(ContentsMenuEntity).filter(ContentsMenuEntity.code == code).first()
        )
        if not entity:
            raise NotFoundException(detail={"message": "해당 메뉴를 찾지 못했습니다."})

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
            ModelConverter.entity_to_model(entity, ContentsMenu) for entity in entities
        ]

    def get_contents_url_list(self, db: Session) -> list[str]:

        entities = db.query(ContentsEntity).all()
        contents_urls: list[str] = [str(entity.contents_url) for entity in entities]
        return contents_urls

    def get_contents_id_url_dict(self) -> dict:

        with self.db() as db:
            entities = db.query(
                ContentsEntity.contents_id,
                ContentsEntity.contents_url
            ).all()
            contents_id_urls: dict = {entity.contents_id: entity.contents_url for entity in entities}
            return contents_id_urls
    
    def get_contents_list(
        self, db: Session, based_on, sort_by, contents_status=None, query=None
    ) -> list[ContentsResponse]:

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

    def get_subject_by_code(self, subject, db: Session) -> ContentsMenu:

        entity = (
            db.query(ContentsMenuEntity)
            .filter(ContentsMenuEntity.code == subject)
            .first()
        )

        if not entity:
            raise NotFoundException(
                detail={"message": "해당하는 menu가 존재하지 않습니다."}
            )

        return ModelConverter.entity_to_model(entity, ContentsMenu)

    def get_contents_detail(self, contents_id, db: Session) -> ContentsResponse:

        entity = (
            db.query(ContentsEntity)
            .filter(
                ContentsEntity.contents_id == contents_id,
                ~ContentsEntity.is_deleted,
            )
            .first()
        )

        if not entity:
            raise NotFoundException(
                detail={"message": "해당하는 콘텐츠가 존재하지 않습니다."}
            )

        return ModelConverter.entity_to_model(entity, ContentsResponse)

    def delete_contents(self, contents_id, db: Session):
        update_statement = (
            update(ContentsEntity)
            .where(ContentsEntity.contents_id == contents_id)
            .values(is_deleted=True)
        )

        db.execute(update_statement)

    def update_contents(
        self, contents_id: int, contents: Contents, db: Session
    ) -> ContentsResponse:
        # merge는 같은 기본 키를 가진 엔티티가 이미 존재하면 업데이트하고, 존재하지 않으면 새로 추가
        updated_entity = db.merge(contents.to_entity())
        db.commit()
        db.refresh(updated_entity)
        return ModelConverter.entity_to_model(updated_entity, ContentsResponse)

    def search_contents_tag(
        self, search_keyword, recsys_model_id, db
    ) -> list[IdWithItem]:

        filter_conditions = [ContentsEntity.contents_status == "published"]

        if recsys_model_id == str(RecommendModels.contents_only_personalized.value):
            filter_conditions.append(ContentsEntity.contents_type == "contents_only")

        if search_keyword:
            keyword = f"%{search_keyword}%"
            filter_conditions.append(ContentsEntity.contents_tags.ilike(keyword))

        results = (
            db.query(
                ContentsEntity.contents_id,
                ContentsEntity.contents_name,
            )
            .filter(~ContentsEntity.is_deleted, *filter_conditions)
            .all()
        )

        return [
            IdWithItem(id=item.contents_id, name=item.contents_name) for item in results
        ]
