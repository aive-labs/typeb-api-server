import base64
from datetime import datetime, timedelta

import aiohttp
from sqlalchemy.orm import Session

from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import Cafe24Exception, NotFoundException
from src.core.transactional import transactional
from src.offers.domain.cafe24_coupon import Cafe24CouponResponse
from src.offers.infra.offer_repository import OfferRepository
from src.offers.routes.dto.response.offer_detail_response import OfferDetailResponse
from src.offers.routes.dto.response.offer_response import OfferResponse
from src.offers.routes.port.get_offer_usecase import GetOfferUseCase
from src.users.domain.user import User


class GetOfferService(GetOfferUseCase):

    def __init__(self, offer_repository: OfferRepository, cafe24_repository: BaseOauthRepository):
        self.offer_repository = offer_repository
        self.cafe24_repository = cafe24_repository
        self.client_id: str = get_env_variable("client_id")
        self.client_secret: str = get_env_variable("client_secret")

    @transactional
    async def get_offers(
        self, based_on, sort_by, start_date, end_date, query, user: User, db: Session
    ) -> list[OfferResponse]:

        if user.mall_id is None:
            raise NotFoundException(detail={"message": "mall 정보가 존재하지 않습니다."})

        token = self.cafe24_repository.get_token(user.mall_id, db)
        access_token = token.access_token
        if self.is_access_token_expired(token):
            url = f"https://{user.mall_id}.cafe24api.com/api/v2/oauth/token"
            payload = f"""grant_type=refresh_token&refresh_token={token.refresh_token}"""
            credentials = f"{self.client_id}:{self.client_secret}".encode()
            encoded_credentials = base64.b64encode(credentials).decode("utf-8")
            authorization_header = f"Basic {encoded_credentials}"
            headers = {
                "Authorization": authorization_header,
                "Content-Type": "application/x-www-form-urlencoded",
            }

            async with aiohttp.ClientSession() as session:
                response = await self.renew_token(url, payload, headers, session)
                cafe24_token_data = Cafe24TokenData(**response)
                self.cafe24_repository.save_tokens(cafe24_token_data, db)
                access_token = cafe24_token_data.access_token

        async with aiohttp.ClientSession() as session:
            # 현재 날짜와 내일 날짜 계산
            today = datetime.now()
            tomorrow = today + timedelta(days=1)

            # 날짜를 문자열로 포맷팅 (YYYY-MM-DD 형식)
            start_date = today.strftime("%Y-%m-%d")
            start_date = "2024-01-01"
            end_date = tomorrow.strftime("%Y-%m-%d")

            url = f"https://{user.mall_id}.cafe24api.com/api/v2/admin/coupons?created_start_date={start_date}&created_end_date={end_date}"
            print(url)
            print(access_token)
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Cafe24-Api-Version": "2024-06-01",
            }
            async with session.get(url=url, headers=headers, ssl=False) as response:
                if response.status != 200:
                    raise Cafe24Exception(
                        detail={
                            "message": "쿠폰 정보를 불러오는데 실패했습니다. 잠시 후에 다시 시도해주세요."
                        }
                    )
                response = await response.json()

                print("cafe24 coupon")
                print(len(response["coupons"]))
                cafe24_coupon_response = Cafe24CouponResponse(**response)
                print(len(cafe24_coupon_response.coupons))
                print(cafe24_coupon_response)

                self.offer_repository.save_new_coupon(cafe24_coupon_response, db)

        offers = self.offer_repository.get_all_offers(
            based_on, sort_by, start_date, end_date, query, db
        )

        offer_responses = [OfferResponse.from_model(offer) for offer in offers]
        return offer_responses

    def is_access_token_expired(self, token):
        return datetime.now() > token.expires_at

    async def renew_token(self, url, payload, headers, session):
        async with session.post(url=url, data=payload, headers=headers, ssl=False) as response:
            response = await response.json()
            return response

    def get_offer_detail(self, coupon_no: str, db: Session) -> OfferDetailResponse:
        offer = self.offer_repository.get_offer_detail(coupon_no, db)
        return OfferDetailResponse.from_model(offer)
