import json
from typing import List

from fastapi import HTTPException

from src.common.utils.get_env_variable import get_env_variable
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.generator.contents_rag import StreamingConversationChain
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.routes.dto.request.contents_generate import ContentsGenerate
from src.contents.routes.port.usecase.generate_contents_usecase import (
    GenerateContentsUseCase,
)
from src.contents.utils.generate_input_handler import (
    ContentQueryHandler,
    get_summary_dict,
)
from src.contents.utils.generation_template import template_dict


class GenerateContentsService(GenerateContentsUseCase):
    """콘텐츠 생성 서비스
    - Db Session을 받아서 콘텐츠 생성을 수행한다.
    - 콘텐츠 생성에 필요한 데이터를 전처리한다.
    """

    def __init__(
        self,
        contents_repository: ContentsRepository,
    ):
        self.contents_repository = contents_repository
        self.template_dict = template_dict
        self.openai_api_key = get_env_variable("openai_api_key")
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

        self.chain = StreamingConversationChain(
            openai_api_key=self.openai_api_key,
            model_name="gpt-4o-mini",
        )

    def _product_resource_handler(
        self,
        product_media_entities: List,
        review_entities: List,
        max_k: int = 3,
    ):
        youtube_resource = [
            entity.link
            for entity in product_media_entities
            if entity.link_type == "youtube"
            if entity.link
        ]

        instagram_resource = [
            entity.link
            for entity in product_media_entities
            if entity.link_type == "instagram"
            if entity.link
        ]

        review_list = [
            {
                "emoji": "💡",
                "message": item.content,
            }
            for item in review_entities
            if item.content
        ][:max_k]

        if len(review_list) > 0:
            review_resource = {"title": "실제 구매하신 분들의 생생한 리뷰", "reviews": review_list}
        else:
            review_resource = {}

        return youtube_resource, instagram_resource, review_resource

    async def _prepare_contents_resource(self, contents_generate: ContentsGenerate, db):

        # instagram 몇개 > 고도화 (views, likes, comments)
        # youtube 몇개 > 고도화 (views, likes, comments)
        # review 몇개 > 고도화 (최근 점수 높은거)
        contents_menu: ContentsMenu = self.contents_repository.get_subject_by_code(
            contents_generate.subject, db
        )
        query = ""
        kwargs_dict = {
            "subject": contents_generate.subject,
            "subject_name": contents_menu.name,
        }
        selected_template = self.template_dict[contents_generate.template]
        try:
            if contents_generate.subject:
                query_handler = ContentQueryHandler(contents_generate.subject, db)
                product_item_cnt = (
                    0
                    if not contents_generate.product_object
                    else len(contents_generate.product_object)
                )
                product_list = (
                    [item.product_code for item in contents_generate.product_object]
                    if product_item_cnt > 0
                    else []
                )
                additional_remark = query_handler.input_data_handler(product_list)
                query = query_handler.get_subject_query()
                if contents_generate.emphasis_context:
                    query += query_handler.add_emphasis(contents_generate.emphasis_context)
                if product_item_cnt > 0:
                    query += query_handler.add_product_data()

                data = (json.dumps(i, ensure_ascii=False) + "\n" for i in additional_remark)
                sample_path = "src/contents/resources/product_data.jsonl"
                with open(sample_path, "w") as f:
                    for line in data:
                        f.write(line)
                if contents_generate.subject not in ["sn000009"]:
                    self.chain.add_docs(sample_path, ".remark")
                else:
                    for item in additional_remark:
                        query += "\n" + item["remark"] + "\n"

            if contents_generate.product_object:
                product_code_list = [item.product_code for item in contents_generate.product_object]
                product_data = self.contents_repository.get_product_from_code(product_code_list, db)
                count_of_rep_nm = len({product.rep_nm for product in product_data})
                # 대표상품명이 1개인 경우에만 summary 코드 생성
                if count_of_rep_nm == 1:
                    summary_dict = get_summary_dict(product_data)
                    kwargs_dict["summary"] = summary_dict
                else:
                    selected_template.replace("__summary__[summary_template], ", "")
                    kwargs_dict["summary"] = ""
                # Additional data
                product_resource_entity = self.contents_repository.get_product_media_resource(
                    product_code_list, db
                )
                review_entity = self.contents_repository.get_product_review(product_code_list, db)
                youtube_resource, insta_resource, review_resource = self._product_resource_handler(
                    product_resource_entity, review_entity
                )

                # Additional data 유무에 따른 템플릿 수정
                if len(youtube_resource) == 0:
                    selected_template.replace(", __youtube__[youtube_uri], __dashed_divider__", "")
                if len(insta_resource) == 0:
                    selected_template.replace(
                        "결론이 끝나면 __divider__, __instagram__[instagram_uri]을 각각 한 줄씩 출력하세요.",
                        "",
                    )
                if len(review_resource) == 0:
                    selected_template.replace(
                        "모든 글이 끝나면 마지막에 __divider__, __review__[reviews]를 각각 한 줄씩 출력하세요.",
                        "",
                    )

                # get image resource
                img_data = self.contents_repository.get_product_img(product_code_list, db)
                img_url = [
                    json.dumps(
                        {
                            "url": f"{self.cloud_front_url}{item.img_path}",
                            "caption": item.creative_tags,
                            "alttext": item.creative_tags,
                        },
                        ensure_ascii=False,
                    )
                    for item in img_data
                ]
                kwargs_dict["youtube_resource"] = (
                    youtube_resource if len(youtube_resource) > 0 else []
                )
                kwargs_dict["insta_resource"] = insta_resource if len(insta_resource) > 0 else []
                if len(review_resource) > 0:
                    review_data = json.dumps(review_resource, ensure_ascii=False)
                else:
                    review_data = {}
                kwargs_dict["review_resource"] = review_data
                kwargs_dict["img_url"] = img_url if len(img_url) > 0 else []

        except Exception as e:
            raise HTTPException(
                status_code=500, detail={"code": "contents/generate", "message": str(e)}
            ) from e

        if contents_generate.additional_prompt:
            selected_template += f"추가 정보 : {contents_generate.additional_prompt}"
        return selected_template, query, kwargs_dict

    async def exec(self, contents_generate: ContentsGenerate, db):
        selected_template, query, kwargs_dict = await self._prepare_contents_resource(
            contents_generate, db
        )
        async for i in self.chain.generate_response(selected_template, query, **kwargs_dict):
            yield i
