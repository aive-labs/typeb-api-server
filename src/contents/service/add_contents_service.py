from pathlib import Path

import aiofiles
from bs4 import BeautifulSoup
from fastapi import HTTPException, UploadFile

from src.contents.domain.contents import Contents
from src.contents.enums.contents_status import ContentsStatus
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.contents.service.add_creatives_service import save_image_asset
from src.users.domain.user import User
from src.users.infra.user_repository import UserRepository
from src.utils.date_utils import localtime_converter, localtime_from_str


class AddContentsService(AddContentsUseCase):

    def __init__(
        self, content_repository: ContentsRepository, user_repository: UserRepository
    ):
        self.content_repository = content_repository
        self.user_repository = user_repository

    async def create_contents(
        self,
        contents_create: ContentsCreate,
        user: User,
        files: UploadFile | None = None,
    ):

        # 콘텐츠 uuid 생성
        uuid = "1234"

        # contents_create
        resource_path = Path("app/resources/")

        # body 태그 내의 모든 텍스트를 추출합니다.
        soup = BeautifulSoup(contents_create.contents_body, "html.parser")
        text_list = [txt.text for txt in soup.find_all("p") if txt is not None]
        body_text = " ".join(text_list)

        image_source = [
            elem["src"] for elem in soup.find_all("img") if elem is not None
        ]
        external_html_body = contents_create.contents_body

        url_from = "https://was.ttalk.biz/creatives"
        url_to = "/assets"
        external_html_body = external_html_body.replace(url_from, url_to)

        resource_domain = "aivelabs.com"
        if files:
            thumbnail = f"{uuid}.png"
            thumbnail_path = resource_path / "contents/thumbnail"

            # save thumbnail
            thumbnail_file_name, thumbnail_path = await save_image_asset(
                files, resource_path=str(thumbnail_path), custom_name=thumbnail
            )
            thumbnail_uri = f"{resource_domain}contents/thumbnail/{thumbnail_file_name}"
        elif len(image_source) > 0:
            thumbnail_uri = image_source[0]
        else:
            thumbnail_uri = resource_domain + "contents/thumbnail/default.png"

        contents_url = "contents_domain" + f"contents/?id={uuid}"
        html_path = f"app/resources/contents/{uuid}.html"

        await save_html(html_path, external_html_body)

        contents_status = ContentsStatus.DRAFT.value

        if contents_create.is_public:
            try:
                # 1. connect ssh client
                # 2. send file to remote path

                pass
            finally:
                pass

        new_style_code = (
            [item.style_cd for item in contents_create.sty_cd]
            if contents_create.sty_cd
            else []
        )

        contents = Contents(
            name=contents_create.contents_name,
            status=contents_status,
            body=contents_create.contents_body,
            plain_text=body_text,
            style_code=new_style_code,
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
            created_at=localtime_converter(),
            updated_by=user.username,
            updated_at=localtime_converter(),
        )

        self.content_repository.add_contents(contents=contents)

        return {"status": "success", "res": "res"}


async def save_html(html_path, body):
    if isinstance(body, str):
        body = body.encode("utf-8")
    try:
        async with aiofiles.open(html_path, "wb") as f:
            await f.write(b"""{% extends 'base.html' %}\n""")
            await f.write(b"""{% block content %}\n""")
            await f.write(body)
            await f.write(b"""\n""")
            await f.write(b"""{% endblock %}""")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"code": "contents/create", "message": str(e)}
        ) from e
