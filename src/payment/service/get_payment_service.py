from sqlalchemy.orm import Session

from src.main.transactional import transactional
from src.payment.routes.use_case.get_payment import CustomerKeyUseCase
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.user.domain.user import User


class CustomerKeyService(CustomerKeyUseCase):

    def __init__(self, payment_repository: BasePaymentRepository):
        self.payment_repository = payment_repository

    def get_customer_key(self, mall_id, db: Session) -> str | None:
        return self.payment_repository.get_customer_key(mall_id, db)

    @transactional
    def save_customer_key(self, user: User, customer_key, db: Session):
        self.payment_repository.save_customer_key(user, customer_key, db)
