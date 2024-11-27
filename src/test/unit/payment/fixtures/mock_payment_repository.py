from unittest.mock import MagicMock

from src.common.utils.get_env_variable import get_env_variable
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.users.domain.user import User


def get_mock_payment_repository():
    mock_repository = MagicMock(spec_set=BasePaymentRepository)

    cafe24_orders: list[Cafe24Order] = []
    cafe24_orders.append(
        Cafe24Order(
            order_id="order123",
            cafe24_order_id="cafe24-20180704-100000000",
            order_name="테스트 주문",
            order_amount=1000.00,
            return_url=f"{get_env_variable('order_return_url')}",
            confirmation_url="https://samplemall.cafe24.com/disp/common/myapps/order?signature=BAhpBBMxojw%3D--d1c0134218f0ff3c0f57cb3b57bcc34e6f170727",
            automatic_payment="F",
            currency="KRW",
        )
    )

    def save_cafe24_order(cafe24_order: Cafe24Order, user: User, db):
        cafe24_orders.append(cafe24_order)

    def save_cafe24_payment(payment_result, user: User, db):
        pass

    def existing_order_by_cafe24_order_id(order_id, db):
        existing_order = [order for order in cafe24_orders if order.cafe24_order_id == order_id]
        return len(existing_order) > 0

    mock_repository.save_cafe24_order.side_effect = save_cafe24_order
    mock_repository.save_cafe24_payment.side_effect = save_cafe24_payment
    mock_repository.existing_order_by_cafe24_order_id.side_effect = (
        existing_order_by_cafe24_order_id
    )

    return mock_repository
