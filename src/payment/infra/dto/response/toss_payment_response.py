from typing import Optional

from pydantic import BaseModel

from src.payment.model.payment_method import PaymentMethod
from src.payment.model.payment_status import PaymentStatus
from src.payment.model.payment_type import PaymentType


class CardDetails(BaseModel):
    issuer_code: str
    acquirer_code: str
    number: str
    installment_plan_months: int
    is_interest_free: bool
    interest_payer: Optional[str]
    approve_no: str
    use_card_point: bool
    card_type: str
    owner_type: str
    acquire_status: str
    amount: int


class EasyPayDetails(BaseModel):
    provider: str | None = None
    amount: int | None = None
    discount_amount: int | None = None


class Receipt(BaseModel):
    url: str | None = None


class Checkout(BaseModel):
    url: str | None = None


class Transfer(BaseModel):
    bank_code: str | None = None
    settlement_status: str | None = None


class CashReceipt(BaseModel):
    type: str | None = None
    receipt_key: str | None = None
    issue_number: str | None = None
    receipt_url: str | None = None
    amount: int | None = None
    tax_free_amount: int | None = None


class Cancel(BaseModel):
    transaction_key: str | None = None
    cancel_reason: str | None = None
    tax_exemption_amount: int | None = None
    cancel_at: str | None = None
    easy_pay_discount_amount: int | None = None
    receipt_key: str | None = None
    cancel_amount: int | None = None
    tax_free_amount: int | None = None
    refundable_amount: int | None = None
    cancel_status: str | None = None
    cancel_request_id: str | None = None


class TossPaymentResponse(BaseModel):
    payment_key: str
    order_id: str
    order_name: str
    status: PaymentStatus
    requested_at: str
    approved_at: str
    type: PaymentType

    card: Optional[CardDetails]

    virtual_account: Optional[str]

    # 퀵 계좌이체인 경우, 값이 들어옴
    transfer: Optional[Transfer]
    cash_receipt: Optional[CashReceipt]

    mobile_phone: Optional[str]
    gift_certificate: Optional[str]
    discount: Optional[str]

    # 주문취소인 경우
    cancels: Optional[list[Cancel]] | None = None
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

    @staticmethod
    def from_response(model) -> "TossPaymentResponse":
        card = None
        if model["card"]:
            card = CardDetails(
                issuer_code=model["card"]["issuerCode"],
                acquirer_code=model["card"]["acquirerCode"],
                number=model["card"]["number"],
                installment_plan_months=model["card"]["installmentPlanMonths"],
                is_interest_free=model["card"]["isInterestFree"],
                interest_payer=model["card"]["interestPayer"],
                approve_no=model["card"]["approveNo"],
                use_card_point=model["card"]["useCardPoint"],
                card_type=model["card"]["cardType"],
                owner_type=model["card"]["ownerType"],
                acquire_status=model["card"]["acquireStatus"],
                amount=model["card"]["amount"],
            )

        easy_pay = None
        if model["easyPay"]:
            easy_pay = EasyPayDetails(
                provider=model["easyPay"]["provider"],
                amount=model["easyPay"]["amount"],
                discount_amount=model["easyPay"]["discountAmount"],
            )

        receipt = None
        if model["receipt"]:
            receipt = Receipt(url=model["receipt"]["url"])

        checkout = None
        if model["checkout"]:
            checkout = Checkout(url=model["checkout"]["url"])

        transfer = None
        if model["transfer"]:
            transfer = Transfer(
                bank_code=model["transfer"]["bankCode"],
                settlement_status=model["transfer"]["settlementStatus"],
            )

        cash_receipt = None
        if model["cashReceipt"]:
            cash_receipt = CashReceipt(
                type=model["cashReceipt"]["type"],
                receipt_key=model["cashReceipt"]["receiptKey"],
                issue_number=model["cashReceipt"]["issueNumber"],
                receipt_url=model["cashReceipt"]["receiptUrl"],
                amount=model["cashReceipt"]["amount"],
                tax_free_amount=model["cashReceipt"]["taxFreeAmount"],
            )

        cancels = None
        if model["cancels"]:
            cancels = [
                Cancel(
                    transaction_key=cancel["transactionKey"],
                    cancel_reason=cancel["cancelReason"],
                    tax_exemption_amount=cancel["taxExemptionAmount"],
                    cancel_at=cancel["canceledAt"],
                    easy_pay_discount_amount=cancel["easyPayDiscountAmount"],
                    receipt_key=cancel["receiptKey"],
                    cancel_amount=cancel["cancelAmount"],
                    tax_free_amount=cancel["taxFreeAmount"],
                    refundable_amount=cancel["refundableAmount"],
                    cancel_status=cancel["cancelStatus"],
                    cancel_request_id=cancel["cancelRequestId"],
                )
                for cancel in model["cancels"]
            ]

        return TossPaymentResponse(
            payment_key=model["paymentKey"],
            order_id=model["orderId"],
            order_name=model["orderName"],
            status=model["status"],
            requested_at=model["requestedAt"],
            approved_at=model["approvedAt"],
            type=model["type"],
            card=card,
            virtual_account=model["virtualAccount"],
            transfer=transfer,
            mobile_phone=model["mobilePhone"],
            gift_certificate=model["giftCertificate"],
            cash_receipt=cash_receipt,
            discount=model["discount"],
            cancels=cancels,
            secret=model["secret"],
            easy_pay=easy_pay,
            country=model["country"],
            is_partial_cancelable=model["isPartialCancelable"],
            receipt=receipt,
            checkout=checkout,
            currency=model["currency"],
            total_amount=model["totalAmount"],
            balance_amount=model["balanceAmount"],
            supplied_amount=model["suppliedAmount"],
            vat=model["vat"],
            tax_free_amount=model["taxFreeAmount"],
            method=model["method"],
            version=model["version"],
        )
