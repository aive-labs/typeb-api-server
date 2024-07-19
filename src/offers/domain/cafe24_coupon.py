from __future__ import annotations

from pydantic import BaseModel


class Cafe24Coupon(BaseModel):
    shop_no: int
    coupon_no: str
    coupon_type: str | None = None
    coupon_name: str | None = None
    coupon_description: str | None = None
    created_date: str | None = None
    deleted: str | None = None
    is_stopped_issued_coupon: str | None = None
    pause_begin_datetime: str | None = None
    pause_end_datetime: str | None = None
    benefit_text: str | None = None
    benefit_type: str | None = None
    benefit_price: str | None = None
    benefit_percentage: str | None = None
    benefit_percentage_round_unit: str | None = None
    benefit_percentage_max_price: str | None = None
    include_regional_shipping_rate: str | None = None
    include_foreign_delivery: str | None = None
    coupon_direct_url: str | None = None
    issue_type: str | None = None
    issue_sub_type: str | None = None
    issue_member_join: str | None = None
    issue_member_join_recommend: str | None = None
    issue_member_join_type: str | None = None
    issue_order_amount_type: str | None = None
    issue_order_start_date: str | None = None
    issue_order_end_date: str | None = None
    issue_order_amount_limit: str | None = None
    issue_order_amount_min: str | None = None
    issue_order_amount_max: str | None = None
    issue_order_path: str | None = None
    issue_order_type: str | None = None
    issue_order_available_product: str | None = None
    issue_order_available_category: str | None = None
    issue_anniversary_type: str | None = None
    issue_anniversary_pre_issue_day: str | None = None
    issue_module_type: str | None = None
    issue_review_count: str | None = None
    issue_review_has_image: str | None = None
    issue_quantity_min: str | None = None
    issue_quntity_type: str | None = None
    issue_max_count: str | None = None
    issue_max_count_by_user: str | None = None
    issue_count_per_once: str | None = None
    issued_count: str | None = None
    issue_member_group_no: str | None = None
    issue_member_group_name: str | None = None
    issue_no_purchase_period: str | None = None
    issue_reserved: str | None = None
    issue_reserved_date: str | None = None
    available_date: str | None = None
    available_period_type: str | None = None
    available_begin_datetime: str | None = None
    available_end_datetime: str | None = None
    available_site: str | None = None
    available_scope: str | None = None
    available_day_from_issued: int | None = None
    available_price_type: str | None = None
    available_order_price_type: str | None = None
    available_min_price: str | None = None
    available_amount_type: str | None = None
    available_payment_method: str | None = None
    available_product: str | None = None
    available_product_list: list[int] | None = None  # noqa: W291
    available_category: str | None = None
    available_category_list: list[int] | None = None
    available_coupon_count_by_order: int | None = None
    serial_generate_method: str | None = None
    coupon_image_type: str | None = None
    coupon_image_path: str | None = None
    show_product_detail: str | None = None
    use_notification_when_login: str | None = None
    send_sms_for_issue: str | None = None
    send_email_for_issue: str | None = None


class Cafe24CouponResponse(BaseModel):
    coupons: list[Cafe24Coupon]
