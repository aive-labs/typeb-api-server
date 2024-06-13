# from contextlib import AbstractContextManager
# from typing import Callable
#
# from sqlalchemy.orm import Session
#
# from src.contents.domain.contents_menu import ContentsMenu
# from src.contents.routes.dto.request.contents_generate import ContentsGenerate
# from src.contents.routes.port.usecase.generate_contents_usecase import GenerateContentsUseCase
# from src.contents.service.port.base_contents_repository import BaseContentsRepository
#
#
# class GenerateContents(GenerateContentsUseCase):
#
#     def __init__(self, contents_repository: BaseContentsRepository, db: Callable[..., AbstractContextManager[Session]]):
#         self.contents_repository = contents_repository
#         self.db = db
#     def exec(self, contents_generate: ContentsGenerate):
#
#         # instagram 몇개 > 고도화 (views, likes, comments)
#         # youtube 몇개 > 고도화 (views, likes, comments)
#         # review 몇개 > 고도화 (최근 점수 높은거)
#         contents_menu: ContentsMenu = self.contents_repository.get_subject_by_code(contents_generate.subject)
#         query = ""
#         kwargs_dict = {
#             'subject': contents_generate.subject,
#             'subject_name': contents_menu.name,
#         }
#         try:
#             if contents_generate.subject:
#                 query_handler = ContentQueryHandler(self.db, contents_generate.subject)
#
#                 material_codes = [code for code in (contents_generate.material1, contents_generate.material2) if code]
#
#
#                 material_codes = [
#                     code
#                     for code
#                     in (contents_generate.material1, contents_generate.material2) if code is not None
#                 ]
#                 style_list = [item.style_cd for item in contents_generate.style_object] if len(
#                     contents_generate.style_object) > 0 else []
#                 query_handler.prepare_mapping_object(material_codes, style_list)
#                 additional_remark = query_handler.input_data_handler()
#
#                 query = query_handler.get_subject_query()
#                 if contents_generate.emphasis_context:
#                     query += query_handler.add_emphasis(contents_generate.emphasis_context)
#                 if len(contents_generate.style_object) > 0:
#                     query += query_handler.add_style_data()
#
#                 data = (
#                     json.dumps(i, ensure_ascii=False) + '\n'
#                     for i
#                     in additional_remark
#                 )
#                 sample_path = 'app/resources/sample_data/style_data.jsonl'
#                 with open(sample_path, 'w') as f:
#                     for line in data:
#                         f.write(line)
#                 if contents_generate.subject not in ['sn000008', 'sn000009']:
#                     chain.add_docs(sample_path, '.remark')
#                 else:
#                     for item in additional_remark:
#                         query += '\n' + item['remark'] + '\n'
#
#             if contents_generate.style_object:
#                 style_cd_list = [item.style_cd for item in contents_generate.style_object]
#                 style_data = get_data_from_style_code(db, style_cd_list)
#                 count_of_rep_nm = len(set([style.rep_nm for style in style_data]))
#                 # 대표상품명이 1개인 경우에만 summary 코드 생성
#                 if count_of_rep_nm == 1:
#                     summary_dict = get_summary_dict(style_data)
#                     kwargs_dict['summary'] = summary_dict
#                 else:
#                     selected_template.replace('__summary__[summary_template], ', '')
#                     kwargs_dict['summary'] = ''
#
#                 # Additional data
#                 youtube_resource, insta_resource, review_resource = get_resource_data(db, style_cd_list)
#
#                 # Additional data 유무에 따른 템플릿 수정
#                 if len(youtube_resource) == 0:
#                     selected_template.replace(', __youtube__[youtube_uri], __dashed_divider__', '')
#                 if len(insta_resource) == 0:
#                     selected_template.replace('결론이 끝나면 __divider__, __instagram__[instagram_uri]을 각각 한 줄씩 출력하세요.', '')
#                 if len(review_resource) == 0:
#                     selected_template.replace('모든 글이 끝나면 마지막에 __divider__, __review__[reviews]를 각각 한 줄씩 출력하세요.', '')
#
#                 # get image resource
#                 img_data = get_style_img(db, style_cd_list)
#                 img_url = [
#                     json.dumps({
#                         'url': f'{credentials["resource_domain"]}creatives/{item.image_uri}',
#                         'caption': item.creative_tags,
#                         'alttext': item.creative_tags,
#                     }, ensure_ascii=False)
#                     for item
#                     in img_data
#                 ]
#
#                 kwargs_dict['youtube_resource'] = youtube_resource if len(youtube_resource) > 0 else []
#                 kwargs_dict['insta_resource'] = insta_resource if len(insta_resource) > 0 else []
#                 if len(review_resource) > 0:
#                     review_data = json.dumps(review_resource, ensure_ascii=False)
#                 else:
#                     review_data = {}
#                 kwargs_dict['review_resource'] = review_data
#                 kwargs_dict['img_url'] = img_url if len(img_url) > 0 else []
#             else:
#                 menu_code_info = db.query(ContentsMenu).filter(
#                     ContentsMenu.code.in_(material_codes)
#                 ).all()
#                 keywords = [item.name for item in menu_code_info]
#                 img_data = get_non_style_img(db, keywords)
#                 img_url = [
#                     json.dumps({
#                         'url': f'{credentials["resource_domain"]}creatives/{item.image_uri}',
#                         'caption': item.creative_tags,
#                         'alttext': item.creative_tags,
#                     }, ensure_ascii=False)
#                     for item
#                     in img_data
#                 ]
#                 kwargs_dict['img_url'] = img_url if len(img_url) > 0 else []
#
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500,
#                 detail={"code": "contents/generate", "message": str(e)}
