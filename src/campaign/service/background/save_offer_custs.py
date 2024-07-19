from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter


def save_offer_custs(db, user_obj, campaign_id, background_task):
    try:
        offer_cus_obj = get_offer_custs(db, campaign_id)
        offer_cus_df = DataConverter.convert_query_to_df(offer_cus_obj)

        created_at = localtime_converter()

        if len(offer_cus_df) == 0:
            print("오퍼가 적용된 고객이 존재하지 않습니다.")
            return True

        if len(offer_cus_df[offer_cus_df["cus_cd"].str.contains("TEST")]) > 0:
            print("테스트 고객입니다.")
            return True

        if len(offer_cus_df[offer_cus_df["event_no"] == "2021301000001"]) > 0:
            # 생일 쿠폰의 경우 별도의 매핑 시스템이 존재하므로 offer_custs 저장 및 pos_sync_trigger를 실행하지 않는다.
            return True

        offer_cus_df["comp_cd"] = 5000
        offer_cus_df["br_div"] = "NPC"
        offer_cus_df["created_at"] = created_at
        offer_cus_df["created_by"] = user_obj.user_id
        offer_cus_df["updated_at"] = created_at
        offer_cus_df["updated_by"] = user_obj.user_id

        offer_cus_df = offer_cus_df.replace({np.nan: None})
        aicrm_mileage = offer_cus_df[offer_cus_df["offer_type_code"].isin(["3", "4"])]
        pos = offer_cus_df[~offer_cus_df["offer_type_code"].isin(["3", "4"])]

        # dag trigger run
        offer_cus_coltroller = OfferCusController(config["dag_user"], config["dag_access"])
        background_var = {"campaign_id": campaign_id}

        ##POS: insert & trigger
        if len(pos) > 0:
            print("pos" + str(len(pos)) + " 명")
            pos_dict = pos.to_dict("records")
            db.bulk_insert_mappings(OfferCust, pos_dict)
            db.commit()

            background_task.add_task(
                offer_cus_coltroller.execute_dag, "pos_sync_trigger", background_var
            )
            # offer_cus_coltroller.execute_dag("pos_sync_trigger",background_var )

        ##aicrm-mileage: insert & trigger
        if len(aicrm_mileage) > 0:
            print("aicrm_mileage" + str(len(aicrm_mileage)) + " 명")

            aicrm_mileage_dict = aicrm_mileage.to_dict("records")
            db.bulk_insert_mappings(OfferMileageCustStatus, aicrm_mileage_dict)
            db.commit()

            background_task.add_task(
                offer_cus_coltroller.execute_dag, "mileage_sync_trigger", background_var
            )
            # offer_cus_coltroller.execute_dag("mileage_sync_trigger",background_var )

    except Exception as e:
        print(e)
        db.rollback()
    # finally:
    #     db.close()

    return True
