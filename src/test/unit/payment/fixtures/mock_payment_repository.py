from unittest.mock import MagicMock

from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.users.domain.user import User


def get_mock_payment_repository():
    mock_repository = MagicMock(spec_set=BasePaymentRepository)

    def save_cafe24_order(cafe24_order: Cafe24Order, user: User, db):
        pass

    def save_cafe24_payment(payment_result, user: User, db):
        pass

    def existing_order_by_cafe24_order_id(order_id, db):
        pass

    return mock_repository
