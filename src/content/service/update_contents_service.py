from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.common.utils.date_utils import get_localtime, localtime_from_str
from src.common.utils.file.s3_service import S3Service
from src.common.utils.get_env_variable import get_env_variable
from src.common.utils.string_utils import generate_random_string
from src.content.domain.contents import Contents
from src.content.enums.contents_status import ContentsStatus
from src.content.infra.contents_repository import ContentsRepository
from src.content.infra.dto.response.contents_response import ContentsResponse
from src.content.routes.dto.request.contents_create import ContentsCreate
from src.content.routes.port.usecase.update_contents_usecase import (
    UpdateContentsUseCase,
)
from src.content.utils.create_html import create_contents_html
from src.main.exceptions.exceptions import NotFoundException
from src.main.transactional import transactional
from src.user.domain.user import User
from src.user.infra.user_repository import UserRepository


class UpdateContentsService(UpdateContentsUseCase):

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
    def exec(
        self, contents_id: int, contents_create: ContentsCreate, user: User, db: Session
    ) -> ContentsResponse:

        original_contents = self.contents_repository.get_contents_detail(contents_id, db)
        if not original_contents:
            raise NotFoundException(detail={"message": "해당하는 콘텐츠가 존재하지 않습니다."})

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

        cafe24_info = self.cafe24_repository.get_cafe24_info(str(user.user_id), db=db)
        if cafe24_info is None:
            raise NotFoundException(detail={"message": "연동된 cafe24 계정이 없습니다."})

        mall_id = cafe24_info.mall_id

        # 썸네일 저장
        if contents_create.thumbnail:
            # 썸네일이 있는 경우
            #   - s3_presigned_url 인 경우
            #   - thumbnail이 기존 이미지와 동일한 경우
            replace_url = f"{self.cloud_front_url}/"
            thumbnail_uri = contents_create.thumbnail.replace(replace_url, "")
        elif image_source:
            # 썸네일을 따로 저장하진 않는 경우
            replace_url = f"{self.cloud_front_url}/"
            thumbnail_uri = image_source[0].replace(replace_url, "")
        else:
            thumbnail_uri = f"{mall_id}/contents/thumbnail/default.png"

        contents_url = original_contents.contents_url

        contents_status = ContentsStatus.DRAFT.value
        if contents_create.is_public:
            contents_html = create_contents_html(external_html_body)
            self.s3_service.put_object(key=contents_url, body=contents_html)
            self.s3_service.invalidate_cache(invalidation_path=contents_url)
            contents_status = ContentsStatus.PUBLISHED.value

        new_style_code = (
            [item.style_cd for item in contents_create.sty_cd] if contents_create.sty_cd else []
        )

        contents = Contents(
            contents_id=contents_id,
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

        updated_contents = self.contents_repository.update(contents_id, contents, db)
        updated_contents.set_thumbnail_url(
            f"{self.cloud_front_url}/{updated_contents.thumbnail_uri}"
        )
        updated_contents.set_contents_url(f"{self.cloud_front_url}/{updated_contents.contents_url}")

        return updated_contents
