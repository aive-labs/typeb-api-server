from typing import Optional

from pydantic import BaseModel

from src.payment.enum.payment_method import PaymentMethod
from src.payment.enum.payment_status import PaymentStatus
from src.payment.enum.payment_type import PaymentType


class CardDetails(BaseModel):
    issuer_code: str
    acquirer_code: str
    number: str
    installment_plan_months: int
    is_interest_free: bool
    interest_player: Optional[str]
    approve_no: str
    use_card_point: bool
    card_type: str
    owner_type: str
    acquire_status: str
    receipt_url: str
    amount: int


class EasyPayDetails(BaseModel):
    provider: str
    amount: int
    discount_amount: int


class Receipt(BaseModel):
    url: str


class Checkout(BaseModel):
    url: str


class PaymentResponse(BaseModel):
    payment_key: str
    order_id: str
    order_name: str
    status: PaymentStatus
    requested_at: str
    approved_at: str
    type: PaymentType
    card: Optional[CardDetails]
    virtual_account: Optional[str]
    transfer: Optional[str]
    mobile_phone: Optional[str]
    gift_certificate: Optional[str]
    cash_receipt: Optional[str]
    discount: Optional[str]
    cancels: Optional[str]
    secret: Optional[str]
    easy_pay: Optional[EasyPayDetails]
    country: str
    is_partial_cancelable: bool
    receipt: Optional[Receipt]
    checkout: Optional[Checkout]
    currency: str
    total_amount: int
    balance_amount: int
    supplied_amount: int
    vat: int
    tax_free_amount: int
    method: PaymentMethod
    version: str
