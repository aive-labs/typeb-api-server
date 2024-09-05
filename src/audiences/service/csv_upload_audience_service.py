from src.audiences.routes.port.usecase.csv_upload_usecase import CSVUploadUseCase
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.audiences.utils.csv_sentence_converter import csv_check_sentence_converter


class CSVUploadAudienceService(CSVUploadUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def check_audience_csv_file(self, uploaded_rows, template_enum) -> tuple:
        entity_name = template_enum["source"]
        template_type = template_enum["_name_"]

        res = self.audience_repository.get_actual_list_from_csv(
            uploaded_rows, target_column=template_type, entity=entity_name
        )

        checked_list = [row[0] for row in res[-1]]

        checked_cnt = len(checked_list)
        upload_cnt = len(uploaded_rows)
        checked_shop_cnt = len([row[0] for row in res[0]] if len(res) == 2 else [])

        res_sentence = csv_check_sentence_converter(
            actual_count=checked_cnt,
            upload_count=upload_cnt,
            template_type=template_type,
            checked_shop_cnt=checked_shop_cnt,
        )

        return res_sentence, checked_list
