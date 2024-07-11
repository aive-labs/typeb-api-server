from src.campaign.infra.campaign_repository import CampaignRepository
from src.offers.infra.offer_repository import OfferRepository
from src.offers.routes.dto.request.offer_update import OfferUpdate
from src.offers.routes.port.update_offer_usecase import UpdateOfferUseCase
from src.users.domain.user import User


class UpdateOfferService(UpdateOfferUseCase):

    def __init__(self, offer_repository: OfferRepository, campaign_repository: CampaignRepository):
        self.offer_repository = offer_repository
        self.campaign_repository = campaign_repository

    def update_offer(self, offer_update: OfferUpdate, user: User):
        pass

    #     kst = pytz.timezone("Asia/Seoul")
    #     now_kst = datetime.now(kst).isoformat()
    #     now_kst_datetime = datetime.fromisoformat(now_kst)
    #
    #     self.check_offer_used_in_campaign(offer_update)
    #
    #     self.check_duplicated_event_offer(offer_update)
    #
    #     offer_type_dict = {
    #         v.code: v.description for _, v in OfferType.__members__.items()
    #     }
    #
    #     style_conditions_checker = is_empty_cond(offer_update.offer_style_conditions)
    #     channel_conditions_checker = is_empty_cond(
    #         offer_update.offer_channel_conditions
    #     )
    #
    #     ## 판매유형 체커 ('00', '10', '20', '30') 만 입력 가능
    #     self.check_sales_type(
    #         channel_conditions_checker, offer_update, style_conditions_checker
    #     )
    #
    #     old_offer: Offer = self.offer_repository.get_offer(offer_update.offer_key)
    #
    #     self.validate_offer_type_change(offer_update, old_offer)
    #
    #     prev_offer_style_conditions = old_offer.offer_style_conditions
    #     prev_offer_channel_conditions = old_offer.offer_channel_conditions
    #     prev_dupl_apply_event = old_offer.dupl_apply_event
    #
    #     self.update_old_offer(
    #         now_kst_datetime, offer_type_dict, offer_update, old_offer, user
    #     )
    #
    #     ## STEP1. offer_dupl_apply 업데이트
    #     ## AICRM(정액, 정률)인 경우 업데이트
    #     ## BIZ 요건 : 중복이 가능한 일반 이벤트만 입력 가능
    #     if (
    #         (prev_dupl_apply_event != offer_update.dupl_apply_event)
    #         & (offer_update.offer_type_code in ["1", "2"])
    #         & (offer_update.offer_source == "AICRM")
    #     ):
    #         offer_id = offer_update.offer_id
    #         event_no = offer_update.event_no
    #
    #         self.offer_repository.save_duplicate_offer(
    #             offer_id, event_no, offer_update, now_kst_datetime, user
    #         )
    #
    # def update_old_offer(
    #     self, now_kst_datetime, offer_type_dict, offer_update, old_offer, user
    # ):
    #     if offer_update.offer_source == "AICRM" and offer_update.offer_type_code in [
    #         "3",
    #         "4",
    #     ]:
    #         # 방어로직 AICRM의 마일리지 오퍼인 경우에만 이벤트 리마크 적용(고객이 보는 리마크)
    #         old_offer.event_remark = offer_update.event_remark
    #     old_offer.crm_event_remark = offer_update.crm_event_remark
    #     old_offer.offer_name = offer_update.offer_name
    #     old_offer.offer_type_code = offer_update.offer_type_code  ## Enum으로 변경 저장
    #     old_offer.offer_type_name = offer_type_dict.get(
    #         int(offer_update.offer_type_code), ""
    #     )  # type 변경
    #     old_offer.offer_use_type = offer_update.offer_use_type.value
    #     old_offer.event_str_dt = offer_update.event_str_dt
    #     old_offer.event_end_dt = offer_update.event_end_dt
    #     old_offer.apply_pcs = offer_update.apply_pcs
    #     old_offer.used_count = offer_update.used_count
    #     old_offer.offer_style_conditions = offer_update.offer_style_conditions
    #     old_offer.offer_channel_conditions = offer_update.offer_channel_conditions
    #     old_offer.dupl_apply_event = offer_update.dupl_apply_event
    #     old_offer.updated_at = now_kst_datetime
    #     old_offer.updated_by = user.username
    #     if offer_update.offer_type_code == "3":
    #         old_offer.mileage_str_dt = offer_update.event_str_dt
    #         old_offer.mileage_end_dt = offer_update.event_end_dt
    #     else:
    #         old_offer.mileage_str_dt = offer_update.mileage_str_dt
    #         old_offer.mileage_end_dt = offer_update.mileage_end_dt
    #
    # def validate_offer_type_change(self, offer_update, old_offer):
    #     if offer_update.offer_source == "AICRM" and old_offer.offer_type_code in [
    #         "1",
    #         "2",
    #     ]:
    #         if offer_update.offer_type_code not in ["1", "2"]:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail={
    #                     "code": "offers/type_error",
    #                     "message": "AICRM 전용 정액/정률 오퍼는 정액/정률로만 변경이 가능합니다.",
    #                 },
    #             )
    #     elif offer_update.offer_source == "AICRM" and old_offer.offer_type_code in [
    #         "3",
    #         "4",
    #     ]:
    #         if offer_update.offer_type_code not in ["3", "4"]:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail={
    #                     "code": "offers/type_error",
    #                     "message": "AICRM 전용 마일리지 오퍼는 사전/사후마일리지로만 변경이 가능합니다.",
    #                 },
    #             )
    #
    # def check_sales_type(
    #     self, channel_conditions_checker, offer_update, style_conditions_checker
    # ):
    #     if offer_update.offer_sale_tp and not all(
    #         item in ["00", "10", "20", "30"] for item in offer_update.offer_sale_tp
    #     ):
    #         raise HTTPException(
    #             status_code=400,
    #             detail={
    #                 "code": "offers/list",
    #                 "message": "판매유형은 '00', '10', '20', '30' 중에서만 입력 가능합니다.",
    #             },
    #         )
    #     if (
    #         offer_update.offer_source == "AICRM"
    #         and offer_update.offer_type_code in ["1", "2"]
    #         and (style_conditions_checker or channel_conditions_checker)
    #     ):
    #         raise HTTPException(
    #             status_code=400,
    #             detail={
    #                 "code": "offers/list",
    #                 "message": "오퍼 조건이 비어있습니다. AICRM 전용 정액/정률 오퍼는 스타일 조건과 채널 조건이 필수입니다.",
    #             },
    #         )
    #
    # def check_duplicated_event_offer(self, offer_update):
    #     is_duplicated_event = self.offer_repository.is_existing_duplicated_date_event(
    #         offer_update
    #     )
    #     if is_duplicated_event:
    #         raise HTTPException(
    #             status_code=400,
    #             detail={
    #                 "code": "offers/modify/denied/02",
    #                 "message": "이벤트 기간이 겹치는 Offer가 존재합니다.",
    #             },
    #         )
    #
    # def check_offer_used_in_campaign(self, offer_update):
    #     is_used_in_campaign = (
    #         self.campaign_repository.is_existing_campaign_by_offer_event_no(
    #             offer_update.event_no
    #         )
    #     )
    #     if is_used_in_campaign:
    #         raise HTTPException(
    #             status_code=400,
    #             detail={
    #                 "code": "offers/modify/denied/01",
    #                 "message": "캠페인에서 사용 중인 이벤트 번호는 수정할 수 없습니다.",
    #             },
    #         )
