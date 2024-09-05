from typing import List

from sqlalchemy import and_, case, distinct, func, literal, or_, update
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.common.utils.model_converter import ModelConverter
from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.infra.entity.contents_entity import ContentsEntity
from src.contents.infra.entity.contents_menu_entity import ContentsMenuEntity
from src.contents.infra.entity.creatives_entity import CreativesEntity
from src.core.exceptions.exceptions import NotFoundException
from src.products.infra.entity.comment_master_entity import (
    ProductReviewEntity,
)
from src.products.infra.entity.product_link_entity import ProductLinkEntity
from src.products.infra.entity.product_master_entity import ProductMasterEntity
from src.search.routes.dto.id_with_item_response import IdWithItem


class ContentsSqlAlchemy:

    def add_contents(self, contents: ContentsEntity, db: Session) -> ContentsResponse:
        db.add(contents)
        db.flush()

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

        return [ModelConverter.entity_to_model(entity, ContentsMenu) for entity in entities]

    def get_menu_map(self, code, db: Session) -> list[ContentsMenu]:

        entity = db.query(ContentsMenuEntity).filter(ContentsMenuEntity.code == code).first()
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

        return [ModelConverter.entity_to_model(entity, ContentsMenu) for entity in entities]

    def get_contents_url_list(self, db: Session) -> list[str]:

        entities = db.query(ContentsEntity).all()
        contents_urls: list[str] = [str(entity.contents_url) for entity in entities]
        return contents_urls

    def get_contents_id_url_dict(self, db: Session) -> dict:

        entities = db.query(ContentsEntity.contents_id, ContentsEntity.contents_url).all()
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
            base_query = base_query.filter(ContentsEntity.contents_status == contents_status)
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

        entity = db.query(ContentsMenuEntity).filter(ContentsMenuEntity.code == subject).first()

        if not entity:
            raise NotFoundException(detail={"message": "해당하는 menu가 존재하지 않습니다."})

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
            raise NotFoundException(detail={"message": "해당하는 콘텐츠가 존재하지 않습니다."})

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

    def search_contents_tag(self, search_keyword, recsys_model_id, db) -> list[IdWithItem]:

        filter_conditions = [ContentsEntity.contents_status == "published"]

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

        return [IdWithItem(id=item.contents_id, name=item.contents_name) for item in results]

    def count_contents_by_campaign_id(self, campaign_id, set_group_seqs, db) -> int:
        contents_count = (
            db.query(func.count(distinct(CampaignSetRecipientsEntity.contents_id)))
            .join(
                CampaignSetGroupsEntity,
                and_(
                    CampaignSetRecipientsEntity.campaign_id == CampaignSetGroupsEntity.campaign_id,
                    CampaignSetRecipientsEntity.set_sort_num
                    == CampaignSetGroupsEntity.set_sort_num,
                    CampaignSetRecipientsEntity.group_sort_num
                    == CampaignSetGroupsEntity.group_sort_num,
                ),
            )
            .filter(
                CampaignSetRecipientsEntity.campaign_id == campaign_id,
                CampaignSetGroupsEntity.set_group_seq.in_(set_group_seqs),
            )
            .scalar()
        )

        return contents_count

    def get_product_from_code(self, product_codes: List[str], db) -> List:
        product_entities = (
            db.query(
                ProductMasterEntity.product_code,
                ProductMasterEntity.product_name,
                ProductMasterEntity.rep_nm,
                ProductMasterEntity.category_name,
                ProductMasterEntity.price,
                ProductMasterEntity.summary_description,
                ProductMasterEntity.simple_description,
                ProductMasterEntity.product_tag,
            )
            .filter(ProductMasterEntity.product_code.in_(product_codes))
            .all()
        )

        return product_entities

    def get_product_media_resource(self, product_codes: List[str], db) -> List:
        product_media_entities = (
            db.query(
                ProductLinkEntity.product_code,
                ProductLinkEntity.link_type,
                ProductLinkEntity.link,
            )
            .filter(ProductLinkEntity.product_code.in_(product_codes))
            .all()
        )
        return product_media_entities

    def get_product_review(self, product_codes: List[str], db) -> List:
        review_entities = (
            db.query(
                ProductReviewEntity.product_no,
                ProductReviewEntity.content,
                ProductReviewEntity.rating,
            )
            .join(
                ProductMasterEntity,
                ProductMasterEntity.product_no == ProductReviewEntity.product_no,
            )
            .filter(ProductMasterEntity.product_code.in_(product_codes))
            .order_by(ProductReviewEntity.rating.desc())
            .all()
        )
        return review_entities

    def get_product_img(self, product_codes: List[str], db) -> List:
        product_img_entities = (
            db.query(
                CreativesEntity.style_cd.label("product_code"),
                CreativesEntity.style_object_name.label("product_name"),
                CreativesEntity.image_uri,
                CreativesEntity.image_path,
                CreativesEntity.creative_tags,
            )
            .filter(CreativesEntity.style_cd.in_(product_codes), ~CreativesEntity.is_deleted)
            .all()
        )
        return product_img_entities

    def get_contents_by_tags(
        self, tags, db: Session, keyword: str | None = None
    ) -> list[IdWithItem]:
        if tags is None or len(tags) == 0:
            # tags_list가 None인 경우에는 항상 2로 설정된 것을 사용
            condition = literal(2)
        else:
            contents_tag_patterns = [f"%{contents_tag}%" for contents_tag in tags]

            tag_conditions = or_(
                *[ContentsEntity.contents_tags.like(pattern) for pattern in contents_tag_patterns]
            )

            condition = case(  # pyright: ignore [reportCallIssue]
                (tag_conditions, 1),  # pyright: ignore [reportArgumentType]
                else_=2,
                # Pass the conditions as positional elements
            )

        subquery = (
            db.query(
                ContentsEntity.contents_id,
                ContentsEntity.contents_name,
                ContentsEntity.contents_tags,
                condition.label("tags_yn"),
            )
            .filter(
                ContentsEntity.contents_status == "published",
                ~ContentsEntity.is_deleted,
            )
            .subquery()
        )

        if keyword:
            keyword = f"%{keyword}%"
            subquery = (
                db.query(subquery.c.contents_id, subquery.c.contents_name, subquery.c.tags_yn)
                .filter(subquery.c.contents_tags.ilike(keyword))
                .subquery()
            )

        query = db.query(
            subquery.c.contents_id.label("id"), subquery.c.contents_name.label("name")
        ).order_by(subquery.c.tags_yn)

        return [IdWithItem(id=data.id, name=data.name) for data in query.all()]
