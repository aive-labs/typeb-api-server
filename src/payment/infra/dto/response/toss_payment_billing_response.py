from pydantic import BaseModel


class CardDetails(BaseModel):
    issuer_code: str
    acquirer_code: str
    number: str
    card_type: str
    owner_type: str


class TossPaymentBillingResponse(BaseModel):
    m_id: str
    customer_key: str
    authenticated_at: str
    method: str
    billing_key: str
    card: CardDetails
    card_company: str
    card_number: str

    @staticmethod
    def from_response(model) -> "TossPaymentBillingResponse":
        card_detail = CardDetails(
            issuer_code=model["card"]["issuerCode"],
            acquirer_code=model["card"]["acquirerCode"],
            number=model["card"]["number"],
            card_type=model["card"]["cardType"],
            owner_type=model["card"]["ownerType"],
        )

        return TossPaymentBillingResponse(
            m_id=model["mId"],
            customer_key=model["customerKey"],
            authenticated_at=model["authenticatedAt"],
            method=model["method"],
            billing_key=model["billingKey"],
            card=card_detail,
            card_company=model["cardCompany"],
            card_number=model["cardNumber"],
        )
