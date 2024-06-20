from datetime import datetime, timedelta

import pytest

from src.auth.infra.dto.cafe24_mall_info import Cafe24MallInfo
from src.auth.infra.dto.cafe24_state_token import Cafe24StateToken
from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.contents.domain.creatives import Creatives
from src.contents.enums.image_asset_type import ImageAssetTypeEnum
from src.contents.routes.dto.request.contents_create import StyleObjectBase
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.service.add_creatives_service import AddCreativesService
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository
from src.core.exceptions.exceptions import NotFoundException
from src.users.domain.user import User


class FakeCafe24Repository(BaseOauthRepository):
    def __init__(self):
        self.cafe24_state_token = [
            Cafe24StateToken(mall_id="mall_001", state_token="1234"),
            Cafe24StateToken(mall_id="mall_002", state_token="4444"),
            Cafe24StateToken(mall_id="mall_003", state_token="3333"),
        ]

        self.cafe24_token_data = [
            Cafe24TokenData(
                access_token="token_123456",
                expires_at=datetime.now() + timedelta(hours=2),
                refresh_token="refresh_token_123456",
                refresh_token_expires_at=datetime.now() + timedelta(days=14),
                client_id="client_001",
                mall_id="mall_001",
                user_id="1",
                scopes=["scope1", "scope2", "scope3"],
                issued_at=datetime.now(),
                shop_no="shop_001",
            ),
            Cafe24TokenData(
                access_token="token_789012",
                expires_at=datetime.now() + timedelta(hours=2),
                refresh_token="refresh_token_789012",
                refresh_token_expires_at=datetime.now() + timedelta(days=14),
                client_id="client_002",
                mall_id="mall_002",
                user_id="2",
                scopes=["scope1", "scope4"],
                issued_at=datetime.now(),
                shop_no="shop_002",
            ),
            Cafe24TokenData(
                access_token="token_345678",
                expires_at=datetime.now() + timedelta(hours=2),
                refresh_token="refresh_token_345678",
                refresh_token_expires_at=datetime.now() + timedelta(days=14),
                client_id="client_003",
                mall_id="mall_003",
                user_id="3",
                scopes=["scope2", "scope3", "scope5"],
                issued_at=datetime.now(),
                shop_no="shop_003",
            ),
        ]

    def get_state_token(self, state_token: str) -> Cafe24StateToken:
        for token in self.cafe24_state_token:
            if token.state_token == state_token:
                return token

        raise NotFoundException("state token에 해당하는 데이터를 찾지 못했습니다.")

    def insert_basic_info(self, user_id: str, mall_id: str, state_token: str):
        self.cafe24_state_token.append(
            Cafe24StateToken(mall_id=mall_id, state_token=state_token)
        )

    def save_tokens(self, cafe24_tokens: Cafe24TokenData):
        save_token = None
        for token in self.cafe24_token_data:
            if token.mall_id == cafe24_tokens.mall_id:
                save_token = token

        if not save_token:
            raise NotFoundException("해당 state 토큰을 찾을 수 없습니다.")

        self.cafe24_token_data.append(cafe24_tokens)

    def is_existing_state_token(self, state_token: str) -> Cafe24StateToken:
        for token in self.cafe24_state_token:
            if token.state_token == state_token:
                return token
        raise NotFoundException("해당 state은 유효하지 않습니다.")

    def get_cafe24_info_by_user_id(self, user_id: str) -> Cafe24MallInfo:
        filtered_tokens = list(
            filter(lambda token: token.user_id == user_id, self.cafe24_token_data)
        )

        if len(filtered_tokens) == 0:
            raise NotFoundException("user_id에 해당하는 mall을 찾지 못했습니다.")
        elif len(filtered_tokens) > 1:
            raise Exception("user_id는 1개만 가질 수 있습니다.")
        else:
            entity = filtered_tokens[0]
            return Cafe24MallInfo(
                mall_id=entity.mall_id,
                user_id=str(entity.user_id),
                scopes=entity.scopes,
                shop_no=entity.shop_no,
            )


class FakeCreativesRepository(BaseCreativesRepository):
    def __init__(self):
        self.creatives: list[Creatives] = []
        self.auto_increment_id = 2

        creative_sample_1 = Creatives(
            creative_id=1,
            image_asset_type="type1",
            style_cd="style1",
            style_object_name="object1",
            image_uri="http://example.com/image1.png",
            image_path="/path/to/image1.png",
            creative_tags="tag1,tag2",
            created_at=datetime.now(),
            created_by="user1",
            updated_at=datetime.now(),
            updated_by="user1",
        )

        # 샘플 데이터 2
        creative_sample_2 = Creatives(
            creative_id=2,
            image_asset_type="type2",
            style_cd="style2",
            style_object_name="object2",
            image_uri="http://example.com/image2.png",
            image_path="/path/to/image2.png",
            creative_tags="tag3,tag4",
            created_at=datetime.now(),
            created_by="user2",
            updated_at=datetime.now(),
            updated_by="user2",
        )

        self.creatives.append(creative_sample_1)
        self.creatives.append(creative_sample_2)

        self.styles = [
            StyleObjectBase(style_cd="style001", style_object_name="Modern"),
            StyleObjectBase(style_cd="style002", style_object_name="Vintage"),
            StyleObjectBase(style_cd="style003", style_object_name="Minimalist"),
            StyleObjectBase(style_cd="style004", style_object_name="Bohemian"),
            StyleObjectBase(style_cd="style005", style_object_name="Industrial"),
        ]

        self.creative_base = [
            CreativeBase(
                creative_id=1,
                image_asset_type="type1",
                image_uri="http://example.com/image1.png",
                image_path="/path/to/image1.png",
                sty_cd="style1",
                sty_nm="object1",
                creative_tags="tag1,tag2",
                updated_by="user1",
                updated_at=datetime.now(),
                related_img_uri=["http://example.com/related_image1.png"],
                rep_nm="Representative Name 1",
                year_season="2021-SS",
                it_gb_nm="IT Name 1",
                item_nm="Item Name 1",
                item_sb_nm="Item Subname 1",
                purpose="Purpose 1",
                price=1000,
            ),
            # 샘플 데이터 2
            CreativeBase(
                creative_id=2,
                image_asset_type="type2",
                image_uri="http://example.com/image2.png",
                image_path="/path/to/image2.png",
                sty_cd="style2",
                sty_nm="object2",
                creative_tags="tag3,tag4",
                updated_by="user2",
                updated_at=datetime.now(),
                related_img_uri=["http://example.com/related_image2.png"],
                rep_nm="Representative Name 2",
                year_season="2022-SS",
                it_gb_nm="IT Name 2",
                item_nm="Item Name 2",
                item_sb_nm="Item Subname 2",
                purpose="Purpose 2",
                price=2000,
            ),
        ]

    def find_by_id(self, id: int) -> Creatives:
        for creative in self.creatives:
            if creative.creative_id == id:
                return creative
        raise NotFoundException("Not found CreativesEntity")

    def find_all(
        self, based_on, sort_by, asset_type=None, query=None
    ) -> list[CreativeBase]:
        return self.creative_base

    def get_simple_style_list(self) -> list:
        return self.styles

    def update_creatives(self, creative_id, creative_update_dict: dict) -> Creatives:
        selected_creative = None
        for creative in self.creatives:
            if creative.creative_id == creative_id:
                selected_creative = creative

        if selected_creative is None:
            raise NotFoundException("Creative가 존재하지 않습니다")

        updated_creative = selected_creative.model_copy(update=creative_update_dict)
        return updated_creative

    def create_creatives(self, creatives_list):
        return creatives_list

    def delete(self, creative_id):
        self.creatives = [
            creative
            for creative in self.creatives
            if creative.creative_id != creative_id
        ]


@pytest.fixture
def test_add_creative_service():
    return AddCreativesService(FakeCreativesRepository(), FakeCafe24Repository())


def describe_소재_생성에_성공한다():
    def 스타일이_있는_경우_s3_presigned_url을_발급한다(
        test_add_creative_service: AddCreativesService,
    ):
        creative_create = CreativeCreate(
            image_asset_type=ImageAssetTypeEnum.STYLE_IMAGE,
            style_cd="style1",
            style_object_name="object1",
            creative_tags="tag1,tag2",
            files=["file1.png", "file2.png"],
        )
        user = User(
            user_id=1,
            username="test_user",
            email="test_user@test.com",
            role_id="admin",
            language="ko",
        )

        result = test_add_creative_service.generate_s3_url(creative_create, user)

        assert len(result) == 2
        assert result[0].original_file_name == creative_create.files[0]

        base_url = result[0].s3_presigned_url.split("?")[0]
        parts = base_url.rsplit("/", 1)
        directory_path = parts[0].split("amazonaws.com/")[-1]
        file_name = parts[1].split("_")[-1]
        assert directory_path == f"mall_001/image_asset"
        assert file_name == creative_create.files[0]

    def 스타일이_없는_경우_s3_presigned_url을_발급한다(
        test_add_creative_service: AddCreativesService,
    ):
        creative_create = CreativeCreate(
            image_asset_type=ImageAssetTypeEnum.NON_STYLE_IMAGE,
            style_cd="style1",
            style_object_name="object1",
            creative_tags="tag1,tag2",
            files=["file1.png", "file2.png"],
        )
        user = User(
            user_id=1,
            username="test_user",
            email="test_user@test.com",
            role_id="admin",
            language="ko",
        )

        result = test_add_creative_service.generate_s3_url(creative_create, user)

        assert len(result) == 2
        assert result[0].original_file_name == creative_create.files[0]

        #  "s3_presigned_url": "https://aice-asset-dev.s3.amazonaws.com/tinyhuman/image_asset/non_style_creative/1718095187539522_string.jpg?AWSAccessKeyId=AKIASTSLMMAUIHZF2WA3&Signature=XNLRLhXO71uZk39Fz%2FNRHr9gJPc%3D&Expires=1718095487"
        base_url = result[0].s3_presigned_url.split("?")[0]
        parts = base_url.rsplit("/", 1)
        directory_path = parts[0].split("amazonaws.com/")[-1]
        file_name = parts[1].split("_")[-1]
        assert directory_path == f"mall_001/image_asset"
        assert file_name == creative_create.files[0]

    def 소재를_생성한다():
        pass


def describe_소재를_생성에_실패한다():
    def 소재_생성에_실패한다():
        pass
