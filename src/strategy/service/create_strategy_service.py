import json

from fastapi import HTTPException

from src.audiences.enums.audience_type import AudienceType
from src.strategy.domain.campaign_theme import StrategyTheme, ThemeAudience, ThemeOffer
from src.strategy.domain.strategy import Strategy
from src.strategy.enums.recommend_model import RecommendModels
from src.strategy.enums.strategy_metrics import StrategyMetrics
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.enums.strategy_target import TargetStrategy
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.port.create_strategy_usecase import CreateStrategyUsecase
from src.users.domain.user import User


class CreateStrategyService(CreateStrategyUsecase):
    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    def create_strategy_object(self, strategy_create: StrategyCreate, user: User):
        # 1. 전략명 중복 확인
        strategy_name = strategy_create.strategy_name
        if self.strategy_repository.is_strategy_name_exists(strategy_name):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "strategy/create",
                    "message": "동일한 전략명이 존재합니다.",
                },
            )

        # 2. request에 있는 어떤 아이디를 어떻게 바꿈
        create_json = strategy_create.model_dump_json()
        strategy_req_json = json.loads(create_json)
        audience_ids_lst = self._get_data_value(strategy_req_json, "audience_ids")
        audience_ids_f_lst = self._flat(audience_ids_lst)

        # 3. 요청 타입이 c 이고 어떤 경우에 어쩌고 저쩌고를 함
        if (strategy_create.audience_type_code == "c") and (
            len(audience_ids_f_lst) != len(set(audience_ids_f_lst))
        ):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "strategy/create",
                    "message": "같은 오디언스가 중복으로 사용되었습니다.",
                },
            )

        # 4. 전략 도메인 생성
        # 전략 엔티티 생성 시 user, created, updated 추가해줘야함
        new_strategy = Strategy(
            strategy_name=strategy_create.strategy_name,
            strategy_tags=strategy_create.strategy_tags,
            strategy_metric_code=strategy_create.strategy_metric_code,
            strategy_metric_name=StrategyMetrics(
                strategy_create.strategy_metric_code
            ).description,
            strategy_status_code=StrategyStatus.inactive.value,
            strategy_status_name=StrategyStatus.inactive.description,
            audience_type_code=strategy_create.audience_type_code,
            audience_type_name=AudienceType(
                strategy_create.audience_type_code
            ).description,
            target_group_code=strategy_create.target_group_code,
            target_group_name=TargetStrategy(
                strategy_create.target_group_code
            ).description,
        )

        # 5. DB 저장

        # 6. 캠페인 테마 수만큼 반복
        campaign_themes: list[StrategyTheme] = []
        recommend_model_ids: list[int] = []
        for _idx, theme in enumerate(strategy_create.campaign_themes):
            # 1. 테마모델 중복 점검
            self._check_duplicate_recommend_model(
                recommend_model_id=theme.recsys_model_id,
                recommend_model_list=recommend_model_ids,
            )
            recommend_model_ids.append(theme.recsys_model_id)

            # 2. 세그먼트 캠페인 - 신상품 추천 모델 단독 사용 점검
            self._check_exclusive_new_collection_model(
                recommend_model_list=recommend_model_ids
            )

            # 3. 커스텀 캠페인 - 오퍼 1개 제한
            self._check_single_offer_per_custom_theme(
                audience_type_code=strategy_create.audience_type_code,
                offer_id_list=theme.theme_audience_set.offer_ids,
            )

            theme_audience = [
                ThemeAudience(
                    audience_id=audience_id,
                )
                for audience_id in theme.theme_audience_set.audience_ids
            ]

            theme_offer = [
                ThemeOffer(
                    offer_id=offer_id,
                )
                for offer_id in theme.theme_audience_set.offer_ids
            ]

            campaign_themes.append(
                StrategyTheme(
                    strategy_theme_name=theme.campaign_theme_name,
                    recsys_model_id=theme.recsys_model_id,
                    contents_tags=theme.theme_audience_set.contents_tags,
                    theme_audience=theme_audience,
                    theme_offer=theme_offer,
                )
            )

        #     2. 전략 > 캠페인 테마에 추가
        #       - db에 플러시해서 campaign theme id 얻는 것이 필요
        #     3. 전략 > 캠페인 테마 > 오디언스 매핑 업데이트
        #       - requeset로 전달 받은 값에서 처리
        #     4. 전략 > 캠페인 테마 > 테마 오퍼
        #       - request에서 전달 받은 값으로 처리
        self.strategy_repository.create_strategy(new_strategy, campaign_themes, user)

        # 커밋

        pass

    def _check_duplicate_recommend_model(
        self, recommend_model_id: int, recommend_model_list
    ):
        """Checks for duplicate recommender system model IDs and raises an exception if found."""
        if recommend_model_id != 0 and (recommend_model_id in recommend_model_list):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "strategy/create",
                    "message": "추천 모델이 중복으로 사용되었습니다.",
                },
            )

    def _check_exclusive_new_collection_model(self, recommend_model_list):
        """Checks if the new collection recommendation model is used exclusively and raises an exception if not."""
        if (RecommendModels.new_collection_rec.value in recommend_model_list) and len(
            set(recommend_model_list)
        ) > 1:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "strategy/create",
                    "message": "신상품 추천 모델은 전략 내 단독으로만 사용 가능합니다. (다른 추천 모델 사용 불가)",
                },
            )

    def _check_single_offer_per_custom_theme(self, audience_type_code, offer_id_list):
        if audience_type_code == "c" and len(offer_id_list) > 1:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "strategy/create",
                    "message": "커스텀 전략의 테마 별 오퍼는 1개까지 사용가능합니다.",
                },
            )

    def _item_generator(self, json_input, lookup_key):
        if isinstance(json_input, dict):
            if lookup_key in json_input:
                yield json_input[lookup_key]
            else:
                for v in json_input.values():
                    yield from self._item_generator(v, lookup_key)

        elif isinstance(json_input, list):
            for item in json_input:
                yield from self._item_generator(item, lookup_key)

    def _get_data_value(self, data, data_name):
        """
        {
        data: 'campaign_themes': [
                                    {'campaign_theme_id': 203,
                                    'theme_audience_set': [
                                                            {'theme_audience_map_id': 350,
                                                            'audience_id': 'aud-000066',
                                                            'theme_cond_list': [
                                                                            {'strategy_cond_list_id': 570, 'offer_id': '202311141039-E1', 'purpose_id': 2}
                                                                            ]
                                                            },
                                                            {'theme_audience_map_id': None,
                                                            'audience_id': 'aud-000092',
                                                            'theme_cond_list': [
                                                                            {'strategy_cond_list_id': None, 'offer_id': '202311141101-E2', 'purpose_id': 4}
                                                                            ]
                                                            }
                                                        ]
                                    }
                                ]
                }
        data_name: "campaign_theme_id"
        """
        return [
            value
            for value in self._item_generator(data, data_name)
            if value is not None
        ]

    def _flat(self, pool):
        res = []
        for v in pool:
            if isinstance(v, list) or isinstance(v, tuple):
                res += self._flat(v)
            else:
                res.append(v)
        return res
