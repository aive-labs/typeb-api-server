from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
from src.products.domain.product import Product
from src.products.enums.product_link_type import ProductLinkType
from src.products.infra.entity.product_link_entity import ProductLinkEntity
from src.products.infra.entity.product_master_entity import ProductMasterEntity
from src.products.routes.dto.request.product_link_update import ProductLinkUpdate
from src.products.routes.dto.response.title_with_link import TitleWithLink
from src.products.service.port.base_product_repository import BaseProductRepository


class ProductRepository(BaseProductRepository):

    def get_rep_nms(self, product_id: str, db: Session):
        entities = (
            db.query(PurchaseAnalyticsMasterStyle)
            .filter(PurchaseAnalyticsMasterStyle.sty_cd == product_id)
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

    def get_all_products(self, db: Session):
        pass

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
        if product_link_update.youtube:
            self.upsert_product_link(
                db, product_id, product_link_update.youtube, ProductLinkType.YOUTUBE
            )

        if product_link_update.instagram:
            self.upsert_product_link(
                db, product_id, product_link_update.instagram, ProductLinkType.INSTAGRAM
            )

    def upsert_product_link(self, db, product_id, links, link_type):
        for link in links:
            if link.id:
                insert_statement = insert(ProductLinkEntity).values(
                    product_link_id=link.id,
                    product_code=product_id,
                    link_type=link_type.value,
                    title=link.title,
                    link=link.link,
                )

                upsert_statement = insert_statement.on_conflict_do_update(
                    index_elements=["product_link_id"],  # conflict 대상 열
                    set_={"title": link.title, "link": link.link},  # 업데이트할 열
                )

                db.execute(upsert_statement)
            else:
                db.add(
                    ProductLinkEntity(
                        product_code=product_id,
                        link_type=link_type.value,
                        title=link.title,
                        link=link.link,
                    )
                )
