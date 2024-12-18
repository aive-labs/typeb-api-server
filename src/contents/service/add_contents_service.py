from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.common.utils.date_utils import get_localtime, localtime_from_str
from src.common.utils.file.s3_service import S3Service
from src.common.utils.get_env_variable import get_env_variable
from src.common.utils.string_utils import generate_random_string
from src.contents.domain.contents import Contents
from src.contents.enums.contents_status import ContentsStatus
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.contents.utils.create_html import create_contents_html
from src.core.exceptions.exceptions import NotFoundException
from src.core.transactional import transactional
from src.users.domain.user import User
from src.users.infra.user_repository import UserRepository


class AddContentsService(AddContentsUseCase):
    def __init__(
        self,
        contents_repository: ContentsRepository,
        user_repository: UserRepository,
        cafe24_repository: BaseOauthRepository,
        s3_service: S3Service,
    ):
        self.contents_repository = contents_repository
        self.user_repository = user_repository
        self.cafe24_repository = cafe24_repository
        self.s3_service = s3_service
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

    @transactional
    def create_contents(
        self, contents_create: ContentsCreate, user: User, db: Session
    ) -> ContentsResponse:

        contents_urls = self.contents_repository.get_contents_url_list(db)
        contents_uuids = [url.split("/")[-1] for url in contents_urls]

        new_uuid = str(generate_random_string(5))
        while new_uuid in contents_uuids:
            new_uuid = str(generate_random_string(5))

        # body 태그 내의 모든 텍스트를 추출합니다.
        soup = BeautifulSoup(contents_create.contents_body, "html.parser")
        text_list = [txt.text for txt in soup.find_all("p") if txt is not None]
        body_text = " ".join(text_list)

        image_source = [elem["src"] for elem in soup.find_all("img") if elem is not None]
        external_html_body = contents_create.contents_body

        cafe24_info = self.cafe24_repository.get_cafe24_info(str(user.user_id), db)
        if cafe24_info is None:
            raise NotFoundException(detail={"message": "연동된 cafe24 계정이 없습니다."})

        mall_id = cafe24_info.mall_id

        # 썸네일 저장
        # 썸네일 파일이 있는 경우
        if contents_create.thumbnail:
            # 파일을 저장한다.
            thumbnail_uri = contents_create.thumbnail
        elif image_source:
            # 썸네일을 따로 저장하진 않는 경우
            replace_url = f"{self.cloud_front_url}/"
            thumbnail_uri = image_source[0].replace(replace_url, "")
        else:
            thumbnail_uri = "common/default.png"

        contents_url = f"{mall_id}/contents/{new_uuid}.html"

        contents_status = ContentsStatus.DRAFT.value
        if contents_create.is_public:
            contents_html = create_contents_html(external_html_body)
            self.s3_service.put_object(key=contents_url, body=contents_html)
            contents_status = ContentsStatus.PUBLISHED.value

        new_style_code = (
            [item.style_cd for item in contents_create.sty_cd] if contents_create.sty_cd else []
        )

        contents = Contents(
            contents_name=contents_create.contents_name,
            contents_status=contents_status,
            contents_body=contents_create.contents_body,
            plain_text=body_text,
            sty_cd=new_style_code,
            subject=contents_create.subject,
            material1=contents_create.material1 if contents_create.material1 else None,
            material2=contents_create.material2 if contents_create.material2 else None,
            template=contents_create.template,
            additional_prompt=contents_create.additional_prompt,
            emphasis_context=contents_create.emphasis_context,
            thumbnail_uri=thumbnail_uri,
            contents_url=contents_url,
            publication_start=(
                localtime_from_str(contents_create.publication_start)
                if contents_create.publication_start
                else None
            ),
            publication_end=(
                localtime_from_str(contents_create.publication_end)
                if contents_create.publication_end
                else None
            ),
            contents_tags=(
                contents_create.contents_tags if contents_create.contents_tags else None
            ),
            created_by=user.username,
            created_at=get_localtime(),
            updated_by=user.username,
            updated_at=get_localtime(),
        )

        new_contents = self.contents_repository.add_contents(contents=contents, db=db)
        new_contents.set_thumbnail_url(f"{self.cloud_front_url}/{new_contents.thumbnail_uri}")
        new_contents.set_contents_url(f"{self.cloud_front_url}/{new_contents.contents_url}")

        return new_contents
