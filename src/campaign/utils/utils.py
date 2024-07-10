def set_summary_sententce(set_cus_count, set_df):
    audience_cnt = len(set(set_df["audience_id"]))
    audience_names = ",".join(set(set_df["audience_name"]))
    avg_response_rate = round(set_df["response_rate"].mean(), 1)
    avg_audience_unit_price = round(set_df["audience_unit_price"].mean())

    sentence_1 = f"세트 고객수는 총 {set_cus_count:,} 명입니다."
    sentence_2 = f"{audience_cnt}개의 오디언스({audience_names})로 구성되었습니다."
    sentence_3 = f"해당 오디언스들의 반응률 평균치는 {avg_response_rate}% 입니다."
    sentence_4 = (
        f"해당 오디언스들의 객단가 평균값은 {avg_audience_unit_price:,}원 입니다."
    )

    recipient_descriptions = [sentence_1, sentence_2, sentence_3, sentence_4]

    return recipient_descriptions
