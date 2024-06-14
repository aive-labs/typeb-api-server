from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.routes.port.usecase.get_contents_usecase import GetContentsUseCase


class GetContentsService(GetContentsUseCase):

    def __init__(self, contents_repository: ContentsRepository):
        self.contents_repository = contents_repository

    def get_contents(self, contents_id) -> ContentsResponse:
        contents = self.contents_repository.get_contents_detail(contents_id)
        contents_dict = contents.model_dump()
        return ContentsResponse(**contents_dict)

    def get_subjects(self, style_yn: bool) -> list[ContentsMenuResponse]:
        contents_menu_list = self.contents_repository.get_subject(style_yn)
        return [
            ContentsMenuResponse(code=menu.code, name=menu.name)
            for menu in contents_menu_list
        ]

    def get_with_subject(self, code: str):
        menu_map = self.contents_repository.get_menu_map(code)
        menu_response = {
            "template": [
                ContentsMenuResponse(code=item.code, name=item.name)
                for item in menu_map
                if item.menu_type == "template"
            ],
        }

        unique_material_code = list(
            {item.code[:2] for item in menu_map if item.menu_type == "material"}
        )

        for idx, material_code in enumerate(unique_material_code):
            menu_response[f"material{idx + 1}"] = [
                ContentsMenuResponse(code=item.code, name=item.name)
                for item in menu_map
                if item.code[:2] == material_code
            ]

        return menu_response

    def get_contents_list(
        self, based_on, sort_by, current_page, per_page, query=None
    ) -> PaginationResponse[ContentsResponse]:
        responses = self.contents_repository.get_contents_list(based_on, sort_by, query)

        items = responses[(current_page - 1) * per_page : current_page * per_page]

        pagination = PaginationBase(
            total=len(responses),
            per_page=per_page,
            current_page=current_page,
            total_page=len(responses) // per_page + 1,
        )

        return PaginationResponse[ContentsResponse](items=items, pagination=pagination)
