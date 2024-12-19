from enum import Enum


class SubscriptionStatus(Enum):
    # 사용자가 요금제를 정상적으로 구독 중인 상태
    ACTIVE = "Active"

    # 구독이 일시 중지되었거나 취소된 상태
    INACTIVE = "Inactive"

    # 구독이 시작되기 전에, 아직 활성화되지 않은 상태
    PENDING = "Pending"

    # 구독 기간이 만료되어 더 이상 유효하지 않은 상태
    EXPIRED = "Expired"

    # 사용자가 구독을 취소하여 더 이상 구독이 유효하지 않은 상태
    CANCELLED = "Cancelled"

    # 사용자가 무료 체험 기간 중인 상태
    TRIAL = "Trial"

    # 구독 갱신이 곧 필요한 상태
    RENEWAL_DUE = "Renewal Due"

    # 구독이 일시적으로 중단된 상태
    PAUSED = "Paused"

    # 결제 실패 또는 연체로 인해 구독이 일시적으로 유지되고 있는 상태
    GRACE_PERIOD = "Grace Period"

    # 구독료가 환불되어 구독이 취소된 상태
    REFUNDED = "Refunded"
