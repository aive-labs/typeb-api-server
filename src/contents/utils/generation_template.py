"""
    # t00001: 블로그 (상품 존재)
    # t00002: 뉴스레터 (상품 존재)
    # t00003: 짧은 아티클 (상품 존재)
    # t00004: 포토카드형 (상품 존재)
    # t00005: 블로그 (상품 부재)
    # t00006: 뉴스레터 (상품 부재)
    # t00007: 짧은 아티클 (상품 부재)
    # t00008: 포토카드형 (상품 부재)
"""

template_dict = {
    "t00001": """
        사용자가 입력한 주제에 대한 짧고 재미있는 블로그 글을 생성하세요.
        - 모든 문장은 한글 존댓말로만 작성합니다.
        - 상품명은 "_" 이전까지만 사용하세요.
        - 본문을 여러 단락으로 나누고, 서론 본론 결론으로 자연스럽게 이어지는 하나의 이야기를 작성하세요.
        - 본문은 하나의 주제만으로 짧게 작성하세요.
        - 상품이 2개 이상인 경우에도 종합적으로 하나를 설명하듯 작성하세요.
        - 입력된 상품 정보 중 '_' 전까지의 상품명이 동일하다면, 해당 상품들의 공통점을 활용하여 하나의 상품으로 이야기하세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        제목 뒤에는 __divider__, __summary__[summary_template], __youtube__[youtube_uri], __dashed_divider__를 각각 한 줄씩 추가하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        서론 뒤, 결론 앞에 각각 __image__[img_uri] 를 한 줄씩 추가하세요.
        결론이 끝나면 __divider__, __instagram__[instagram_uri]을 각각 한 줄씩 출력하세요.
        모든 글이 끝나면 마지막에 __divider__, __review__[reviews]를 각각 한 줄씩 출력하세요.
        형식 사이 사이에 줄바꿈을 공백으로 남기지 마세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00002": """
        사용자가 입력한 주제에 대해 설명하는 짧고 재미있는 뉴스레터 글을 생성하세요.
        - 제목, 소제목, 본문(서론, 본론, 결론)만 작성합니다.
        - 글은 최대한 간결하게 작성하되, 핵심 마케팅 포인트를 담고 있어야 합니다.
        - 모든 문장은 한글 존댓말로만 작성합니다.
        - 본문에 '서론', '본론', '결론' 이라는 단어를 사용하지마세요.
        - 상품명은 "_" 이전까지만 사용하세요.
        - 문단마다 소제목을 작성하세요.
        - 상품이 2개 이상인 경우에도 종합적으로 하나를 설명하듯 작성하세요.
        - 입력된 상품 정보 중 '_' 전까지의 상품명이 동일하다면, 해당 상품들의 공통점을 활용하여 하나의 상품으로 이야기하세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        제목 뒤에는 __divider__, __summary__[summary_template], __image__[img_uri], __dashed_divider__를 각각 한 줄씩 추가하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        __subhead__소제목은 여기에 작성하세요.
        본문 단락 사이사이에 __image__[img_uri] 를 한 줄씩 추가하세요.
        모든 글이 끝나면 마지막에 __divider__, __review__[reviews]를 각각 한 줄씩 출력하세요.
        형식 사이 사이에 줄바꿈을 공백으로 남기지 마세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00003": """
        사용자가 입력한 주제에 대한 3~4문장 정도의 짧은 아티클을 생성하세요.
        - 모든 문장은 한글 존댓말로만 작성합니다.
        - 상품명은 "_" 이전까지만 사용하세요.
        - 역슬래시를 사용하지 마세요.
        - 사실이 아닌 정보를 추가하지 마세요.
        - 상품이 2개 이상인 경우에도 종합적으로 하나를 설명하듯 작성하세요.
        - 입력된 상품 정보 중 '_' 전까지의 상품명이 동일하다면, 해당 상품들의 공통점을 활용하여 하나의 상품으로 이야기하세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        제목 뒤에는 __divider__, __image__[img_uri]를 각각 한 줄씩 추가하세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00004": """
        사용자가 입력한 주제에 대해 눈길을 끄는 제목과 특징을 설명하는 짧은 문장들을 작성하세요.
        - json 형식이 아닙니다.
        - 상품에 대해 가볍게 설명하는 단일 문장을 4~5개 출력하세요. 짧고 간략할수록 좋습니다.
        - 상품명 내 "_"를 포함한 이후 글자는 제외하세요. 상품명을 만들어내지 마세요.
        - 상품이 2개 이상인 경우에도 종합적으로 하나를 설명하듯 작성하세요.
        - 입력된 상품 정보 중 '_' 전까지의 상품명이 동일하다면, 해당 상품들의 공통점을 활용하여 하나의 상품으로 이야기하세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        제목 뒤에는 __divider__를 한 줄 추가하세요.
        모든 문장 앞에는 __image__[img_uri]를 한 줄씩 추가하세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00005": """
        주어진 정보만 이용하여 짧고 재미있는 블로그 글을 생성하세요.
        - 모든 문장은 한글 존댓말로만 작성합니다.
        - 역슬래시를 사용하지 마세요.
        - 주어지지 않은 이야기는 하지 마세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        제목 뒤에는 __divider__를 한 줄 추가하세요.
        서론 뒤, 결론 앞에 각각 __image__[img_uri] 를 한 줄씩 추가하세요.
        형식 사이 사이에 줄바꿈을 공백으로 남기지 마세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00006": """
        주어진 정보를 이용하여 사용자가 입력한 주제에 대해 설명하는 짧고 재미있는 뉴스레터 글을 생성하세요.
        - 제목, 소제목, 본문(서론, 본론, 결론)만 작성합니다.
        - 글은 최대한 간결하게 작성하되, 핵심 마케팅 포인트를 담고 있어야 합니다.
        - 모든 문장은 한글 존댓말로만 작성합니다.
        - 역슬래시를 사용하지 마세요.
        - 사실이 아닌 정보를 추가하지 마세요.
        - 문단마다 소제목을 작성하세요.
        - 소제목에는 서론, 본론, 결론 이라는 단어를 사용하지 마세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        __subhead__소제목은 여기에 작성하세요.
        제목 뒤에는 __divider__, __image__[img_uri]를 각각 한 줄씩 추가하세요.
        본문 단락 사이사이에 __image__[img_uri] 를 한 줄씩 추가하세요.
        형식 사이 사이에 줄바꿈을 공백으로 남기지 마세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00007": """
        주어진 정보를 이용하여 사용자가 입력한 주제에 대해 정보를 전달해주는 3~4문장 정도의 짧은 아티클을 생성하세요.
        - 모든 문장은 한글 존댓말로만 작성합니다.
        - 역슬래시를 사용하지 마세요.
        - 사실이 아닌 정보를 추가하지 마세요.
        - 아래 데이터를 읽고 요약하여 사용하세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        각 문단이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        제목 뒤에는 __divider__, __image__[img_uri]를 각각 한 줄씩 추가하세요.

        주제 : {question}
        정보 : {context}
        """,
    "t00008": """
        주어진 정보를 이용하여 사용자가 입력한 주제에 대해 정보를 전달하는 3~4개의 문장 혹은 어구를 생성하세요.
        - 눈길을 끄는 제목을 함께 생성하세요.
        - json 형식이 아닙니다.
        - 문장들은 이어지지 않아도 됩니다.
        - 꼭 필요한 정보를 전달하세요.

        아래의 형식에 맞춰 출력하세요. 단, [] 안에 있는 내용은 절대 변경하지말고 그대로 출력하세요. 고정값입니다.
        __title__제목은 여기에 작성하세요.
        생성된 문장 혹은 어구 단락이 시작할때 항상 __text__를 앞에 포함해서 작성해주세요.
        제목 뒤에는 __divider__를 한 줄 추가하고, 모든 문장 혹은 어구의 앞에 __image__[img_uri]를 한 줄씩 추가하세요.

        주제 : {question}
        정보 : {context}
        """,
}
