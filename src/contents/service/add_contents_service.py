import aiofiles
from bs4 import BeautifulSoup
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.common.utils.get_env_variable import get_env_variable
from src.contents.domain.contents import Contents
from src.contents.enums.contents_status import ContentsStatus
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.core.exceptions import NotFoundError
from src.users.domain.user import User
from src.users.infra.user_repository import UserRepository
from src.utils.date_utils import localtime_converter, localtime_from_str
from src.utils.file.s3_service import S3Service
from src.utils.utils import generate_random_string


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

    async def create_contents(self, contents_create: ContentsCreate, user: User):

        contents_urls = self.contents_repository.get_contents_url_list()
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

        # url_from = "https://was.ttalk.biz/creatives"
        # url_to = "/assets"
        # external_html_body = external_html_body.replace(url_from, url_to)

        cafe24_info = self.cafe24_repository.get_cafe24_info_by_user_id(
            str(user.user_id)
        )
        if cafe24_info is None:
            raise NotFoundError("연동된 cafe24 계정이 없습니다.")

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
            thumbnail_uri = f"{mall_id}/contents/thumbnail/default.png"

        contents_url = f"{mall_id}/contents/{new_uuid}.html"

        contents_status = ContentsStatus.DRAFT.value
        if contents_create.is_public:
            contents_html = create_contents_html(external_html_body)
            self.s3_service.put_object(key=contents_url, body=contents_html)
            contents_status = ContentsStatus.PUBLISHED.value

        new_style_code = (
            [item.style_cd for item in contents_create.sty_cd]
            if contents_create.sty_cd
            else []
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
            created_at=localtime_converter(),
            updated_by=user.username,
            updated_at=localtime_converter(),
        )

        self.contents_repository.add_contents(contents=contents)

        # return contents


def create_contents_html(body: str) -> str:
    body_bytes = body.encode("utf-8")

    html_content = (
        b"{% extends 'base.html' %}\n"
        b"{% block content %}\n" + body_bytes + b"\n"
        b"{% endblock %}"
    )

    env = Environment(
        loader=FileSystemLoader(
            searchpath="src/contents/resources/html_template"
        ),  # 템플릿 파일이 위치한 경로 설정
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.from_string(html_content.decode("utf-8"))
    return template.render()


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
