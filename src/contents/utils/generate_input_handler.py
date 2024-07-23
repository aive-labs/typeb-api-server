import json
from typing import List
from src.products.infra.entity.product_master_entity import ProductMasterEntity
from fastapi.encoders import jsonable_encoder

class ContentQueryHandler:
    def __init__(self, subject_code, db):
        self.db = db
        self.subject_code = subject_code
        ## subject_code에 따른 쿼리를 생성하기 위한 딕셔너리, TypeB에서는 상품소개, 자유주제만 우선 사용
        self.subject_query_dict = {
            'ss000001': """아래 주어진 상품(들)을 소개하세요.""",
            'ss000002': """주어진 데이터를 활용하여 {material1}과 함께 상품(들)을 소개하는 글을 작성하세요.
                트레킹 코스명에 대한 이야기를 주로 하고, 상품에 대한 이야기는 20% 정도만 하세요. 볼거리나 특징을 하나하나 자세히 설명할 필요 없습니다. 유명한 몇가지에 대해서만 집중하세요.""",
            'ss000003': """먼저 주어진 산에 대한 이야기를 10문장 이내로 요약하고, {material1}과 함께 상품(들)을 소개하는 글을 작성하세요.
                제목은 산에 대해 흥미를 끌 수 있도록 15글자 이내로 작성하세요. 명산에 대한 이야기를 80% 하고, 상품에 대한 이야기는 20% 정도만 하세요.
                다른 산들과 비교되는 독특한 점이나 볼거리, 실제 산행 시 도움이 될 이야기 등에 대해 주로 이야기하고, 역사나 이름에 대한 설명 등 재미없는 이야기들은 모두 제외하세요. 
                이 글을 읽고 바로 산에 가고 싶어질 수 있도록 쉽고 재미있게 이야기하세요.""",
            'ss000004': """먼저 주어진 등산 코스에 대한 이야기를 10문장 이내로 요약하고, {material1}과 함께 상품(들)을 소개하는 글을 작성하세요.
                제목은 등산에 흥미를 끌 수 있도록 15글자 이내로 작성하세요.산에 대한 이야기를 80% 하고, 상품에 대한 이야기는 20% 정도만 하세요.
                독특한 점이나 볼거리, 실제 산행 시 도움이 될 이야기 등에 대해 주로 이야기하고, 역사나 이름에 대한 설명 등 재미없는 이야기들은 모두 제외하세요. 
                이 글을 읽고 바로 산에 가고 싶어질 수 있도록 쉽고 재미있게 이야기하세요.""",
            'ss000005': """주어진 데이터를 활용하여 {material1}을 소개하고, 이와 함께 상품(들)에 대한 이야기를 전개하세요.
                제목은 상품명이 들어가지 않아도 됩니다. 흥미를 끌 수 있도록 15글자 이내로 작성하세요.{material1}에 대한 이야기를 80% 하고, 
                상품에 대한 이야기는 20% 정도만 하세요.어려운 단어는 사용하지 말고, 어린 아이도 이해할 수 있을 정도로 쉽고 재미있게 작성하세요.""",
            'sn000001': """주어진 데이터를 활용하여 {material1}을 소개하는 글을 작성하세요.
                볼거리나 특징을 하나하나 자세히 설명할 필요 없습니다. 
                유명한 몇가지에 대해서만 집중하세요.""",
            'sn000002': """먼저 주어진 산에 대한 이야기를 10문장 이내로 요약하고, 
                {material1}을 소개하는 글을 작성하세요.제목은 산에 대해 흥미를 끌 수 있도록 15글자 이내로 작성하세요.
                다른 산들과 비교되는 독특한 점이나 볼거리, 실제 산행 시 도움이 될 이야기 등에 대해 주로 이야기하고, 
                역사나 이름에 대한 설명 등 재미없는 이야기들은 모두 제외하세요. 이 글을 읽고 바로 산에 가고 싶어질 수 있도록 쉽고 재미있게 이야기하세요.""",
            'sn000003': """먼저 주어진 등산 코스에 대한 이야기를 10문장 이내로 요약하고, 
                {material1}을 소개하는 글을 작성하세요.
                제목은 등산에 흥미를 끌 수 있도록 15글자 이내로 작성하세요.
                독특한 점이나 볼거리, 실제 산행 시 도움이 될 이야기 등에 대해 주로 이야기하고, 역사나 이름에 대한 설명 등 재미없는 이야기들은 모두 제외하세요.
                이 글을 읽고 바로 산에 가고 싶어질 수 있도록 쉽고 재미있게 이야기하세요.""",
            'sn000004': """주어진 데이터를 활용하여 {material2}을 소개하는 글을 작성하세요.제목은 트레킹 코스에 대한 이야기를 주로 하고, 
                사람들의 눈길을 끌 수 있도록 하세요.
                트레킹 코스에 대한 설명을 하며 주어진 {material1}에 대한 이야기도 함께 하세요.
                볼거리나 특징을 하나하나 자세히 설명할 필요 없습니다. 유명한 몇가지에 대해서만 집중하세요.""",
            'sn000005': """먼저 주어진 산에 대한 이야기를 10문장 이내로 요약하고, 
                {material2}을 소개하는 글을 작성하세요. 제목은 산에 대해 흥미를 끌 수 있도록 15글자 이내로 작성하세요.
                산을 소개하며 주어진 {material1}에 대해서도 소개해보세요. 다른 산들과 비교되는 독특한 점이나 볼거리, 
                실제 산행 시 도움이 될 이야기 등에 대해 주로 이야기하고, 역사나 이름에 대한 설명 등 재미없는 이야기들은 모두 제외하세요. 
                이 글을 읽고 바로 산에 가고 싶어질 수 있도록 쉽고 재미있게 이야기하세요.""",
            'sn000006': """먼저 주어진 등산 코스에 대한 이야기를 10문장 이내로 요약하고, 
                {material2}을 소개하는 글을 작성하세요.제목은 등산에 흥미를 끌 수 있도록 15글자 이내로 작성하세요.
                등산에 대해 이야기하며 주어진 {material1}에 대해 이야기하세요.
                독특한 점이나 볼거리, 실제 산행 시 도움이 될 이야기 등에 대해 주로 이야기하고, 역사나 이름에 대한 설명 등 재미없는 이야기들은 모두 제외하세요. 
                이 글을 읽고 바로 산에 가고 싶어질 수 있도록 쉽고 재미있게 이야기하세요.""",
            'sn000007': """아래 주어진 데이터를 활용하여 {material1}에 대한 쉽고 재미있는 글을 작성하세요.""",
            'sn000008': """아래 주어진 데이터를 활용하여 {material1}에 대한 쉽고 재미있는 글을 작성하세요.""",
            'sn000009': """아래 주어진 데이터를 활용하여 재미있는 글을 작성하세요.""",
        }

        self.docu_column_mapper = {
            'product_master': {
                'table_class' : ProductMasterEntity,
                'columns': {
                    'product_name': '[상품명]',
                    'rep_nm': '[시리즈명]',
                    'category_name': '[카테고리]',
                    'price': '[현재가]',
                    # 'summary_description': '[요약설명]',
                    # 'simple_description': '[간단설명]',
                    # 'product_tag': '[상품태그]',
                    # 'additional_description': '추가설명',
                },
                'codes': [
                    'ss000001',
                    'ss000002',
                    'ss000003',
                    'ss000004',
                    'ss000005',
                ]
            },
        }
    
    # def prepare_mapping_object(self, material_codes: List[str]=[], style_list: List[str]=[]):
    #     """query, input 정보를 생성하기 이전에 기본데이터를 준비하는 메서드
    #     """
    #     self.material_codes = material_codes
    #     self.style_list = style_list

    #     menu_code_info = self.db.query(ContentsMenu).filter(
    #         ContentsMenu.code.in_(material_codes)
    #     ).all()
        
    #     self.material_info = [
    #         {
    #             'name': item.name,
    #             'code': item.code,
    #         }
    #         for item
    #         in menu_code_info
    #     ]
    #     # 방어로직: code가 ti로 시작하면 리스트에서 뒤로 옮김
    #     self.material_info = sorted(self.material_info, key=lambda x: x['code'].startswith('ti'))

    def get_subject_query(self):
        """템플릿 코드에 따라서 헤드 프롬프트를 매핑하여 반환
        
        Returns:
            str: material name이 반영된 쿼리 생성
        """
        if self.subject_code in ['ss000001', 'sn000009']:
            self.query = self.subject_query_dict.get(self.subject_code)
        else:
            raise Exception('subject_code가 잘못되었습니다.')

        return self.query

    def add_emphasis(self, text:str):
        """텍스트에 강조 영역을 추가하는 함수

        Args:
            text (str): 강조 영역을 추가할 텍스트

        Returns:
            str: 강조영역 문구
        """
        # {강조 영역}을 메인 주제로 이야기해주세요.
        if text != '':    
            return f"""[강조 영역]을 반영해서 작성해주세요.
            [강조 영역]
            {text}"""
        else:
            return text


    def add_product_data(self):
        """상품 데이터를 추가하는 함수
        스타일명에 _W, _M이 포함되어 있으면 삭제하고, 하나의 상품명으로 합침

        Args:
            product_name (List[str]): 스타일 데이터

        Returns:
            str: 스타일 영역 전처리 문구
        """
        if self.product_name_list:
            products = []
            for product in self.product_name_list:
                if '_W' in product or '_M' in product:
                    product = product.replace('_W', ' 여성').replace('_M', ' 남성')
                products.append(product)

            return f"""상품 : {','.join(set(products))}"""
        else:
            raise Exception('상품명 데이터가 없습니다. input_data_handler를 먼저 실행해주세요')
    

    def input_data_handler(self, product_list=List[str]|None):
        """입력 데이터를 전처리하는 함수
        """
        # self.subject_code 가 포함된 docu_column_mapper의 key를 찾아서 해당 데이터를 가져옴
        subject_codes = [k for k, v in self.docu_column_mapper.items() if self.subject_code in v.get('codes')]

        # subject_code에 해당하는 데이터가 없으면 에러
        # if len(subject_codes)==0:
        #     raise Exception('subject_code에 해당하는 데이터가 없습니다.')

        self.remark = []
        if self.subject_code == 'ss000001':
            self.product_list = product_list
            for idx, subject in enumerate(subject_codes):
                object_data = []
                if idx > 0:
                    handle_string += '\n'

                if subject == 'product_master':
                    if len(self.product_list) == 0:
                        raise Exception('product_list가 비어있습니다.')
                    object_data = self.db.query(self.docu_column_mapper.get(subject).get('table_class')).filter(
                        ProductMasterEntity.product_code.in_(self.product_list)
                    ).all()

                    self.product_name_list = [object.product_name for object in object_data]

                if len(object_data) > 0:
                    for additional_data_object in object_data:
                        handle_string = ''
                        dict_obj = dict(jsonable_encoder(additional_data_object))
                        for k, v in self.docu_column_mapper.get(subject).get('columns').items():
                            if dict_obj.get(k):
                                handle_string += f"{v} {dict_obj.get(k)}\n"
                        self.remark.append({'remark': handle_string})
        else:
            self.remark.append({'remark': ''})
        return self.remark


def get_summary_dict(head_product):
    find_keys = {
        'product_name': '상품명',
        'rep_nm': '시리즈명',
        'category_name': '종류',
        'price': '현재가'
    }
    word_mapper = {'F':'여성','M':'남성','U':'남녀공용'}
    # rep_nm_remove_key = ['size_range', 'colors']

    head_product = [head_product._mapping for head_product in head_product]

    # if len(head_product) > 1:
    #     # remove size_range key in find_keys
    #     for remove_key in rep_nm_remove_key:
    #         find_keys.pop(remove_key)

    product_dict = {}
    for k, v in find_keys.items():
        product_dict[v] = []
        for product_tuple in head_product:
            if product_tuple.get(k):
                product_dict[v].append(
                    word_mapper.get(product_tuple[k], product_tuple[k])
                )
    res_list = [
        [k, ','.join(set(v))]
        for k, v
        in product_dict.items() if len(v) > 0
    ]
    
    return json.dumps(res_list, ensure_ascii=False)