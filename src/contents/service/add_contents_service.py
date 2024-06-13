import aiofiles
from bs4 import BeautifulSoup
from fastapi import HTTPException

from src.contents.domain.contents import Contents
from src.contents.enums.contents_status import ContentsStatus
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.users.domain.user import User
from src.users.infra.user_repository import UserRepository
from src.utils.date_utils import localtime_converter, localtime_from_str
from src.utils.utils import generate_random_string


class AddContentsService(AddContentsUseCase):
    def __init__(
        self, content_repository: ContentsRepository, user_repository: UserRepository
    ):
        self.content_repository = content_repository
        self.user_repository = user_repository

    async def create_contents(self, contents_create: ContentsCreate, user: User):

        contents_urls = self.content_repository.get_contents_url_list()
        contents_uuids = [url.split("=")[-1] for url in contents_urls]

        new_uuid = str(generate_random_string(5))
        while new_uuid in contents_uuids:
            new_uuid = str(generate_random_string(5))

        # contents_create
        # resource_path = Path("app/generator/")

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

        # 썸네일 저장
        # 썸네일 파일이 있는 경우
        if contents_create.file:
            # 파일을 저장한다.
            pass
        elif image_source:
            # 썸네일을 따로 저장하진 않는 경우
            thumbnail_uri = image_source[0]
        else:
            thumbnail_uri = resource_domain + "contents/thumbnail/default.png"

        # save html
        contents_domain = "s3.amazonaws.com"
        contents_url = f"{contents_domain}/contents/?id={new_uuid}"
        html_path = f"app/resources/contents/{new_uuid}.html"
        # 파일로 html을 저장
        await save_html(html_path, external_html_body)

        contents_status = ContentsStatus.DRAFT.value
        # root_source = "app/resources/image_asset"
        if contents_create.is_public:
            # s3에 저장하자!
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

        return contents


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
