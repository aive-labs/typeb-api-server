from sqlalchemy.orm import Session

from src.content.domain.contents import Contents
from src.content.domain.contents_menu import ContentsMenu
from src.content.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.content.infra.dto.response.contents_response import ContentsResponse
from src.content.service.port.base_contents_repository import BaseContentsRepository
from src.search.model.id_with_item_response import IdWithItem


class ContentsRepository(BaseContentsRepository):

    def __init__(self, contents_sqlalchemy: ContentsSqlAlchemy):
        self.contents_sqlalchemy = contents_sqlalchemy

    def add_contents(self, contents: Contents, db: Session) -> ContentsResponse:
        return self.contents_sqlalchemy.add_contents(contents.to_entity(), db)

    def get_subject(self, style_yn, db: Session) -> list[ContentsMenu]:
        return self.contents_sqlalchemy.get_subject(style_yn, db)

    def get_menu_map(self, code, db: Session) -> list[ContentsMenu]:
        return self.contents_sqlalchemy.get_menu_map(code, db)

    def get_contents_list(self, db: Session, based_on, sort_by, query) -> list[ContentsResponse]:
        return self.contents_sqlalchemy.get_contents_list(db, based_on, sort_by, query=query)

    def get_contents_id_url_dict(self, db: Session) -> dict:
        return self.contents_sqlalchemy.get_contents_id_url_dict(db)

    def get_subject_by_code(self, subject: str, db: Session) -> ContentsMenu:
        return self.contents_sqlalchemy.get_subject_by_code(subject, db)

    def get_contents_url_list(self, db: Session) -> list[str]:
        return self.contents_sqlalchemy.get_contents_url_list(db)

    def get_contents_detail(self, contents_id: int, db: Session) -> ContentsResponse:
        return self.contents_sqlalchemy.get_contents_detail(contents_id, db)

    def delete(self, contents_id: int, db: Session):
        self.contents_sqlalchemy.delete_contents(contents_id, db)

    def update(self, contents_id: int, contents: Contents, db: Session) -> ContentsResponse:
        return self.contents_sqlalchemy.update_contents(contents_id, contents, db)

    def search_contents_tag(self, keyword, recsys_model_id, db: Session) -> list[IdWithItem]:
        return self.contents_sqlalchemy.search_contents_tag(keyword, recsys_model_id, db)

    def count_contents_by_campaign_id(self, campaign_id, set_group_seqs, db: Session) -> int:
        return self.contents_sqlalchemy.count_contents_by_campaign_id(
            campaign_id, set_group_seqs, db
        )

    def get_product_from_code(self, product_code, db: Session):
        return self.contents_sqlalchemy.get_product_from_code(product_code, db)

    def get_product_media_resource(self, product_code, db: Session):
        return self.contents_sqlalchemy.get_product_media_resource(product_code, db)

    def get_product_review(self, product_code, db: Session):
        return self.contents_sqlalchemy.get_product_review(product_code, db)

    def get_product_img(self, product_code, db: Session):
        return self.contents_sqlalchemy.get_product_img(product_code, db)

    def get_contents_by_tags(self, contents_tags, db: Session, keyword=None) -> list[IdWithItem]:
        return self.contents_sqlalchemy.get_contents_by_tags(contents_tags, db, keyword)
