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
