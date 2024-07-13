from sqlalchemy import func, update
from sqlalchemy.orm import Session

from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
from src.products.domain.product import Product
from src.products.enums.product_link_type import ProductLinkType
from src.products.infra.entity.product_link_entity import ProductLinkEntity
from src.products.infra.entity.product_master_entity import ProductMasterEntity
from src.products.routes.dto.request.product_link_update import ProductLinkUpdate
from src.products.routes.dto.request.product_update import ProductUpdate
from src.products.routes.dto.response.title_with_link import TitleWithLink
from src.products.service.port.base_product_repository import BaseProductRepository


class ProductRepository(BaseProductRepository):

    def get_rep_nms(self, product_id: str, db: Session):
        entities = (
            db.query(PurchaseAnalyticsMasterStyle)
            .filter(PurchaseAnalyticsMasterStyle.product_code == product_id)
            .all()
        )
        rep_nm_list = list({entity.rep_nm for entity in entities})
        return rep_nm_list

    def get_product_detail(self, product_id: str, db: Session) -> Product:
        entity = (
            db.query(ProductMasterEntity)
            .filter(ProductMasterEntity.product_code == product_id)
            .first()
        )
        return Product.model_validate(entity)

    def get_all_products(
        self, based_on: str, sort_by: str, current_page: int, per_page: int, db: Session
    ) -> list[Product]:
        sort_col = getattr(ProductMasterEntity, based_on)
        if sort_by == "desc":
            sort_col = sort_col.desc()
        else:
            sort_col = sort_col.asc()

        entities = (
            db.query(ProductMasterEntity)
            .order_by(sort_col)
            .offset((current_page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return [Product.model_validate(entity) for entity in entities]

    def get_all_products_count(self, db) -> int:
        return db.query(func.count(ProductMasterEntity.product_code)).scalar()

    def get_links_by_product_code(
        self, product_id: str, link_type: str, db: Session
    ) -> list[TitleWithLink]:
        entities = (
            db.query(ProductLinkEntity)
            .filter(
                ProductLinkEntity.product_code == product_id,
                ProductLinkEntity.link_type == link_type,
            )
            .all()
        )

        return [
            TitleWithLink(
                id=str(entity.product_link_id), title=entity.title, link=entity.link
            )
            for entity in entities
        ]

    def update_product_link(
        self, product_id, product_link_update: ProductLinkUpdate, db
    ):

        if product_link_update.youtube is not None:
            self.upsert_product_link(
                db, product_id, product_link_update.youtube, ProductLinkType.YOUTUBE
            )

        if product_link_update.instagram is not None:
            self.upsert_product_link(
                db, product_id, product_link_update.instagram, ProductLinkType.INSTAGRAM
            )

    def upsert_product_link(self, db, product_id, links, link_type):

        db.query(ProductLinkEntity).filter(
            ProductLinkEntity.product_code == product_id,
            ProductLinkEntity.link_type == link_type.value,
        ).delete()
        db.flush()

        for link in links:
            if link.id:
                db.merge(
                    ProductLinkEntity(
                        product_link_id=int(link.id),
                        product_code=product_id,
                        link_type=link_type.value,
                        title=link.title,
                        link=link.link,
                    )
                )
            else:
                db.add(
                    ProductLinkEntity(
                        product_code=product_id,
                        link_type=link_type.value,
                        title=link.title,
                        link=link.link,
                    )
                )

    def update(self, product_id, product_update: ProductUpdate, db):
        update_statement = (
            update(ProductMasterEntity)
            .where(ProductMasterEntity.product_code == product_id)
            .values(
                {
                    "rep_nm": product_update.rep_nm,
                    "comment": product_update.comment,
                    "recommend_yn": product_update.recommend_yn.value,
                }
            )
        )

        db.execute(update_statement)
