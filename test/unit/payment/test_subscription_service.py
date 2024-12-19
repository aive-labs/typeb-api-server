from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dateutil.relativedelta import relativedelta

from src.payment.domain.subscription import Subscription, SubscriptionPlan
from src.payment.model.subscription_status import SubscriptionStatus
from src.user.domain.user import User


@pytest.fixture
def default_user():
    return User(
        user_id=1,
        username="테스트",
        password="테스트",
        email="test@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        brand_name_ko="브랜드",
        brand_name_en="brand",
        language="ko",
        cell_phone_number="010-1234-1234",
        test_callback_number="010-1234-1234",
        mall_id="aivelabs",
    )


def test__구독이_없으면_신규_구독을_생성한다(cafe24_payment_service, mock_db, default_user):
    cafe24_payment_service.pay_for_subscription(default_user, mock_db)

    cafe24_payment_service.subscription_repository.get_plans.assert_called_once()
    cafe24_payment_service.subscription_repository.register_subscription.assert_called_once()


def test__만료된_구독이_있으면_현재_시점_기준_1개월_후_만료되는_구독을_생성한다(
    cafe24_payment_service, mock_db, default_user
):
    cafe24_payment_service.subscription_repository.get_my_subscription = MagicMock(
        return_value=Subscription(
            id=1,
            plan_id=1,
            start_date=datetime.now() - relativedelta(months=3),
            end_date=datetime.now() - relativedelta(months=2),
            auto_renewal=False,
            last_payment_date=datetime.now() - relativedelta(months=3),
            created_by="aivelabs",
            created_at=datetime.now() - relativedelta(months=3),
            status=SubscriptionStatus.ACTIVE.value,
            plan=SubscriptionPlan(
                id=1,
                name="1개월",
                price=30000,
                description="한달 일별캠페인의 집행 금액 평균의 합계가 100만원 이하입니다.",
            ),
        )
    )

    cafe24_payment_service.pay_for_subscription(default_user, mock_db)
    cafe24_payment_service.subscription_repository.update_subscription.assert_called_once()
    cafe24_payment_service.subscription_repository.register_subscription.assert_not_called()


def test__구독이_있으면_기간을_1개월_연장한다(cafe24_payment_service, mock_db, default_user):
    cafe24_payment_service.subscription_repository.get_my_subscription = MagicMock(
        return_value=Subscription(
            id=1,
            plan_id=1,
            start_date=datetime(2024, 12, 1),
            end_date=datetime.now() + relativedelta(months=1),
            auto_renewal=False,
            last_payment_date=datetime(2024, 12, 1),
            created_by="aivelabs",
            created_at=datetime(2024, 12, 1),
            status=SubscriptionStatus.ACTIVE.value,
            plan=SubscriptionPlan(
                id=1,
                name="1개월",
                price=30000,
                description="한달 일별캠페인의 집행 금액 평균의 합계가 100만원 이하입니다.",
            ),
        )
    )

    cafe24_payment_service.pay_for_subscription(default_user, mock_db)
    cafe24_payment_service.subscription_repository.update_subscription.assert_called_once()
    cafe24_payment_service.subscription_repository.register_subscription.assert_not_called()
