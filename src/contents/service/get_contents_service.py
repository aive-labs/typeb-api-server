from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.contents.routes.port.usecase.get_contents_usecase import GetContentsUseCase


class GetContentsService(GetContentsUseCase):

    def __init__(self, contents_repository: ContentsRepository):
        self.contents_repository = contents_repository

    def get_contents(self):
        pass

    def get_subjects(self, style_yn: bool) -> list[ContentsMenuResponse]:
        contents_menu_list = self.contents_repository.get_subject(style_yn)
        return [
            ContentsMenuResponse(code=menu.code, name=menu.name)
            for menu in contents_menu_list
        ]
