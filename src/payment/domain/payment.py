from pydantic import BaseModel

from src.payment.enum.payment_method import PaymentMethod
from src.payment.enum.payment_status import PaymentStatus
from src.payment.enum.payment_type import PaymentType
from src.payment.enum.product import ProductType
from src.payment.infra.dto.response.toss_payment_response import TossPaymentResponse
from src.payment.infra.entity.payment_entity import PaymentEntity
from src.users.domain.user import User


class Payment(BaseModel):
    payment_key: str
    order_id: str
    order_name: str
    status: PaymentStatus
    requested_at: str
    approved_at: str
    type: PaymentType
    card_number: str | None = None
    card_type: str | None = None
    receipt_url: str | None = None
    checkout_url: str | None = None
    currency: str
    total_amount: int
    balance_amount: int
    supplied_amount: int
    vat: int
    tax_free_amount: int
    method: PaymentMethod
    version: str
    product_name: str

    def to_entity(self, user: User) -> "PaymentEntity":
        return PaymentEntity(
            payment_key=self.payment_key,
            order_id=self.order_id,
            order_name=self.order_name,
            status=self.status.value,
            requested_at=self.requested_at,
            approved_at=self.approved_at,
            type=self.type.value,
            card_number=self.card_number,
            card_type=self.card_type,
            receipt_url=self.receipt_url,
            checkout_url=self.checkout_url,
            currency=self.currency,
            total_amount=self.total_amount,
            balance_amount=self.balance_amount,
            supplied_amount=self.supplied_amount,
            vat=self.vat,
            tax_free_amount=self.tax_free_amount,
            method=self.method.value,
            version=self.version,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

    @staticmethod
    def from_toss_response(response: TossPaymentResponse, product_type: ProductType):
        return Payment(
            payment_key=response.payment_key,
            order_id=response.order_id,
            order_name=response.order_name,
            status=response.status,
            requested_at=response.requested_at,
            approved_at=response.approved_at,
            type=response.type,
            card_number=response.card.number if response.card else None,
            card_type=response.card.card_type if response.card else None,
            receipt_url=response.receipt.url if response.receipt else None,
            checkout_url=response.checkout.url if response.checkout else None,
            currency=response.currency,
            total_amount=response.total_amount,
            balance_amount=response.balance_amount,
            supplied_amount=response.supplied_amount,
            vat=response.vat,
            tax_free_amount=response.tax_free_amount,
            method=response.method,
            version=response.version,
            product_name=product_type.value,
        )
