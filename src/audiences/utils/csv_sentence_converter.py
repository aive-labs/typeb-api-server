from src.audiences.enums.csv_template import CsvTemplates


def csv_check_sentence_converter(
    actual_count, template_type, upload_count, checked_shop_cnt=None
):
    if template_type == CsvTemplates.cus_cd.name:
        result_sentence = (
            f"{upload_count}개의 고객목록 중 {actual_count:,}개가 확인됐습니다."
        )
    elif template_type == CsvTemplates.shop_cd.name:
        result_sentence = f"{upload_count}개의 주관리 매장 중 {checked_shop_cnt:,}개가 확인되었으며, {checked_shop_cnt:,}개의 주관리 매장에 해당되는 고객번호 {actual_count:,}개가 확인되었습니다."
    else:
        raise ValueError("Invalid message_template type provided")
    return result_sentence
