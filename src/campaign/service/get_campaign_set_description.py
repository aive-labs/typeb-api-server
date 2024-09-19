from collections import defaultdict

from sqlalchemy import Integer, cast, func, literal
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.delivery_cost_vendor_entity import (
    DeliveryCostVendorEntity,
)
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.add_set_rep_contents import (
    add_set_rep_contents,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets import get_campaign_sets
from src.campaign.routes.dto.response.campaign_set_description_response import (
    CampaignSetDescription,
    CampaignSetDescriptionResponse,
)
from src.campaign.routes.port.get_campaign_set_description_usecase import (
    GetCampaignSetDescriptionUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.utils.data_converter import DataConverter
from src.core.exceptions.exceptions import NotFoundException


class GetCampaignSetDescription(GetCampaignSetDescriptionUseCase):
    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    def exec(self, campaign_id: str, db: Session) -> CampaignSetDescriptionResponse:
        # 해당 세트의 매체비용 리셋 - step3에서 메세지 사용여부를 수정했을 수 있으므로 매체비용을 다시 계산한다.
        db.query(CampaignSetsEntity).filter(
            CampaignSetsEntity.campaign_id == campaign_id,
        ).update({CampaignSetsEntity.media_cost: None})

        campaign_sets = [row._asdict() for row in get_campaign_sets(campaign_id, db)]

        for set_elem in campaign_sets:
            medias = set_elem["medias"]  # tms,kft
            rep_medias = (
                medias.replace("kft", "카카오 친구톡")
                .replace("kat", "카카오 알림톡")
                .replace("tms", "문자 메세지")
            )
            set_elem["medias"] = rep_medias

        set_groups = [row._asdict() for row in get_campaign_set_groups(campaign_id, db)]

        campaign_sets = add_set_rep_contents(campaign_sets, set_groups, campaign_id, db)

        # 매체비용, 발송수, 콘텐츠
        ##발송사, 건당 비용
        ##세트별 매체비용, 발송수 , 콘텐츠
        ##to-do 발송수
        campaign_obj = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        if campaign_obj is None:
            raise NotFoundException(detail={"message": "캠페인 정보를 찾지 못했습니다."})

        shop_send_yn = campaign_obj.shop_send_yn

        set_media_cost = [
            row._asdict()
            for row in self.get_set_description(
                shop_send_yn,
                campaign_id,
                db,
            )
        ]
        campaign_sets = DataConverter.merge_dict_by_key(
            campaign_sets, set_media_cost, key_field="set_seq"
        )

        # 사용체크된 세트 그룹만 필터
        use_campaign_sets = [
            set_dict for set_dict in campaign_sets if set_dict["media_cost"] is not None
        ]

        # 해당 세트의 매체비용 업데이트
        for set_elem in use_campaign_sets:
            db.query(CampaignSetsEntity).filter(
                CampaignSetsEntity.campaign_id == campaign_id,
                CampaignSetsEntity.set_seq == set_elem["set_seq"],
            ).update({CampaignSetsEntity.media_cost: set_elem["media_cost"]})

        db.commit()

        return CampaignSetDescriptionResponse(
            campaign_set=[
                CampaignSetDescription(**campaign_set) for campaign_set in use_campaign_sets
            ]
        )

    def convert_to_set_group_message_list(self, set_group_messages):

        result_dict = defaultdict(list)
        # {set_seq: dict()}
        for item in set_group_messages:
            set_seq = item["set_seq"]
            result_dict[set_seq].append(item)

        result_dict = dict(result_dict)

        for k, _ in result_dict.items():
            # k -> set_seq
            set_group_list = result_dict[k]
            total_list = []
            for g_idx, _ in enumerate(set_group_list):
                # g_idx -> set_group index
                set_group_messages = result_dict[k][g_idx].copy()

                if len(total_list) == 0:
                    sub_dict = {}
                    sub_dict["set_group_seq"] = set_group_messages["set_group_seq"]
                    sub_dict["group_sort_num"] = set_group_messages["group_sort_num"]
                    sub_dict["set_seq"] = set_group_messages["set_seq"]
                    set_group_messages.pop("set_group_seq")
                    sub_dict["campaign_msg"] = (
                        set_group_messages
                        if set_group_messages["msg_send_type"] == "campaign"
                        else None
                    )

                    if sub_dict["campaign_msg"]:
                        sub_dict["campaign_msg"]["rec_explanation"] = set_group_messages[
                            "rec_explanation"
                        ]

                    sub_dict["remind_msg_list"] = (
                        [set_group_messages]
                        if set_group_messages["msg_send_type"] == "remind"
                        else None
                    )

                    if sub_dict["remind_msg_list"]:
                        for i, _ in enumerate(sub_dict["remind_msg_list"]):
                            sub_dict["remind_msg_list"][i]["remind_seq"] = set_group_messages[
                                "remind_seq"
                            ]

                    total_list.append(sub_dict)

                else:
                    # total_list에 이미 있는 set_group_seq를 제외한 set_group_seq 리스트
                    set_group_seqs = list({elem_dict["set_group_seq"] for elem_dict in total_list})

                    if set_group_messages["set_group_seq"] not in set_group_seqs:
                        sub_dict = {}
                        sub_dict["set_group_seq"] = set_group_messages["set_group_seq"]
                        sub_dict["group_sort_num"] = set_group_messages["group_sort_num"]
                        sub_dict["set_seq"] = set_group_messages["set_seq"]
                        set_group_messages.pop("set_group_seq")

                        sub_dict["campaign_msg"] = (
                            set_group_messages
                            if set_group_messages["msg_send_type"] == "campaign"
                            else None
                        )

                        if sub_dict["campaign_msg"]:
                            sub_dict["campaign_msg"]["rec_explanation"] = set_group_messages[
                                "rec_explanation"
                            ]

                        sub_dict["remind_msg_list"] = (
                            [set_group_messages]
                            if set_group_messages["msg_send_type"] == "remind"
                            else None
                        )

                        if sub_dict["remind_msg_list"]:
                            for i, _ in enumerate(sub_dict["remind_msg_list"]):
                                sub_dict["remind_msg_list"][i]["remind_seq"] = set_group_messages[
                                    "remind_seq"
                                ]

                        total_list.append(sub_dict)

                    else:
                        # total_list에 이미 있는 set_group_seq가 있는 경우 append

                        total_list_index = None
                        for idx, elem_dict in enumerate(total_list):

                            if elem_dict["set_group_seq"] == set_group_messages["set_group_seq"]:
                                total_list_index = idx

                        set_group_messages.pop("set_group_seq")

                        # 리마인드 메세지가 들어온 경우
                        if set_group_messages["msg_send_type"] == "remind":

                            if total_list[total_list_index]["remind_msg_list"]:
                                # 리마인드 메세지가 1개 이상 들어와 있는 경우
                                total_list[total_list_index]["remind_msg_list"].append(
                                    set_group_messages
                                )
                            else:
                                # 리마인드 메세지가 새로 들어오는 경우
                                total_list[total_list_index]["remind_msg_list"] = [
                                    set_group_messages
                                ]

                        # 캠페인 메세지가 들어온 경우
                        elif set_group_messages["msg_send_type"] == "campaign":
                            total_list[total_list_index]["campaign_msg"] = set_group_messages

            # 1개 set_seq에 대한 group_message 할당 완료
            result_dict[k] = total_list

        return result_dict

    def get_set_description(self, shop_send_yn, campaign_id: str, db: Session):
        # 발송사
        msg_delivery_vendor_value = (
            db.query(CampaignEntity.msg_delivery_vendor)
            .filter(CampaignEntity.campaign_id == campaign_id)
            .scalar()
        )

        msg_delivery_vendor = literal(msg_delivery_vendor_value)

        # 메세지별 매체비용
        subquery = (
            db.query(
                SetGroupMessagesEntity.set_group_msg_seq,
                SetGroupMessagesEntity.set_group_seq,
                SetGroupMessagesEntity.msg_type,
                msg_delivery_vendor.label("msg_delivery_vendor"),
            )
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.is_used == True,
            )
            .subquery()
        )

        role_delivery_c_vender = (
            db.query(DeliveryCostVendorEntity)
            .filter(DeliveryCostVendorEntity.shop_send_yn == shop_send_yn)
            .subquery()
        )
        subquery1 = (
            db.query(
                subquery.c.set_group_msg_seq,
                subquery.c.set_group_seq,
                subquery.c.msg_type,
                subquery.c.msg_delivery_vendor,
                role_delivery_c_vender.c.cost_per_send,
            )
            .join(
                role_delivery_c_vender,
                (subquery.c.msg_delivery_vendor == role_delivery_c_vender.c.msg_delivery_vendor)
                & (subquery.c.msg_type == role_delivery_c_vender.c.msg_type),
            )
            .subquery()
        )

        # 그룹별 메세지별 비용
        group_subquery = (
            db.query(CampaignSetGroupsEntity)
            .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
            .subquery()
        )

        group_subquery = (
            db.query(
                CampaignSetGroupsEntity.set_group_seq,
                CampaignSetGroupsEntity.set_seq,
                (subquery1.c.cost_per_send * CampaignSetGroupsEntity.recipient_group_count).label(
                    "media_cost"
                ),
            )
            .join(subquery1, CampaignSetGroupsEntity.set_group_seq == subquery1.c.set_group_seq)
            .subquery()
        )

        res = db.query(
            group_subquery.c.set_seq,
            cast(func.sum(group_subquery.c.media_cost), Integer).label("media_cost"),
        ).group_by(group_subquery.c.set_seq)

        return res.all()
