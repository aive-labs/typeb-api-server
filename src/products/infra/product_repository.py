from sqlalchemy.orm import Session

from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
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
