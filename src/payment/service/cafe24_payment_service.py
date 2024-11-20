from sqlalchemy.orm import Session

from src.payment.routes.dto.request.payment_request import PaymentRequest
from src.payment.routes.use_case.payment import PaymentUseCase
from src.users.domain.user import User


class Cafe24PaymentService(PaymentUseCase):
    async def exec(self, user: User, db: Session, payment_request: PaymentRequest | None = None):
        pass
