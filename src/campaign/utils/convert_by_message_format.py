import numpy as np
import pandas as pd

from src.message_template.model.message_type import MessageType


def convert_send_msg_type(row):
    if row["send_msg_type"] in ("sms", "lms", "mms"):

        if row["send_filecount"] > 0:
            return "mms"
        elif len(row["send_msg_body"]) + len(row["bottom_text"]) < 45:
            return "sms"
        else:
            return "lms"

    else:
        return row["send_msg_type"]


def convert_by_message_format(df: pd.DataFrame, kakao_sender_key: str):
    # 발송사, 메세지 타입에 따른 기타 변수 생성

    ## kakao
    ## 카카오발신프로필 kakao_send_profile_key
    kakao_msg_type = [
        MessageType.KAKAO_ALIM_TEXT.value,  # 알림톡 기본형
        MessageType.KAKAO_TEXT.value,  # 친구톡 이미지형에 이미지가 없는경우
        MessageType.KAKAO_IMAGE_GENERAL.value,  # 친구톡 이미지형
        MessageType.KAKAO_IMAGE_WIDE.value,  # 친구톡 와이드 이미지형
        MessageType.KAKAO_CAROUSEL.value,
    ]

    df["kko_yellowid"] = kakao_sender_key
    df["kko_send_timeout"] = 60

    # 대체 발송
    # kat -> lms
    # kft -> (광고) + lms
    ##kakao friend
    kakao_friend_msg = [
        MessageType.KAKAO_TEXT.value,  # 친구톡 이미지형에 이미지가 없는경우
        MessageType.KAKAO_IMAGE_GENERAL.value,  # 친구톡 이미지형
        MessageType.KAKAO_IMAGE_WIDE.value,  # 친구톡 와이드 이미지형
        MessageType.KAKAO_CAROUSEL.value,
    ]

    cond_resend = [
        (df["send_msg_type"] == MessageType.KAKAO_ALIM_TEXT.value),  # lms
        (df["send_msg_type"].isin(kakao_friend_msg)),  # lms
        ~(df["send_msg_type"].isin(kakao_msg_type)),  # tms -> 대체 메세지 없음
    ]

    choice_resend_type = ["lms", "lms", None]  # tms -> 대체 메세지 없음

    choice_resend_body = [
        df["send_msg_body"],
        "(광고)" + df["send_msg_body"] + "\n\n" + df["bottom_text"],
        None,  # tms -> 대체 메세지 없음
    ]

    df["kko_resend_type"] = np.select(cond_resend, choice_resend_type)
    df["kko_resend_msg"] = np.select(cond_resend, choice_resend_body)

    # 카카오친구톡광고표시
    cond_kft = [
        (df["send_msg_type"].isin(kakao_friend_msg)),
        ~(df["send_msg_type"].isin(kakao_friend_msg)),
    ]

    choice_kft = ["Y", None]
    df["kko_ft_adflag"] = np.select(cond_kft, choice_kft)

    # 카카오친구톡 템플릿 키
    choice_kft_template = ["SSG_KFT_CRM", df["kko_template_key"]]  # 고정값
    df["kko_template_key"] = np.select(cond_kft, choice_kft_template)

    ##kakao friend - wide
    kakao_friend_wide_msg = [MessageType.KAKAO_IMAGE_WIDE.value]  # 친구톡 와이드 이미지형

    # 카카오친구톡와이드이미지사용
    cond_kft = [
        (df["send_msg_type"].isin(kakao_friend_wide_msg)) & (df["send_filecount"] > 0),
        (df["send_msg_type"].isin(kakao_friend_wide_msg)) & (df["send_filecount"] == 0),
        ~(df["send_msg_type"].isin(kakao_friend_wide_msg)),
    ]

    choice_kft = ["Y", "N", None]  # 친구톡 와이드 x & 이미지(o,x)
    df["kko_ft_wideimg"] = np.select(cond_kft, choice_kft)

    ##kakao alim
    # 카카오알림톡 기본형
    df["kko_at_type"] = None

    ##msg_type 변환
    cond_msg_tp = [
        df["send_msg_type"] == "kakao_alim_text",  # 알림톡
        (df["send_msg_type"] == "kakao_image_wide")
        & (df["kko_ft_wideimg"] == "Y"),  # 친구톡와이드 & 이미지 O
        (df["send_msg_type"] == "kakao_image_general")
        & (df["send_filecount"] > 0),  # 친구톡 & 이미지 O
        (df["send_msg_type"] == "kakao_image_wide")
        & (df["kko_ft_wideimg"] != "Y"),  # 친구톡와이드 & 이미지 X
        (df["send_msg_type"] == "kakao_text"),  # 친구톡 텍스트
        (df["send_msg_type"] == "kakao_image_general")
        & (df["send_filecount"] == 0),  # 친구톡 & 이미지 X
        df["send_msg_type"] == "kakao_carousel",  # 친구톡 캐러셀
        (df["send_msg_type"].isin(["sms", "lms", "mms"])),  # 문자메세지
    ]

    choice_msg_tp = [
        "at",  # 알림톡
        "fw",  # 친구톡와이드 & 이미지 O
        "fi",  # 친구톡 & 이미지 O
        "ft",  # 친구톡와이드 & 이미지 X,
        "ft",  # 카카오 텍스트
        "ft",  # 친구톡 & 이미지 X
        "fc",  # 친구톡 캐러셀
        df["send_msg_type"],
    ]
    df["send_msg_type"] = np.select(cond_msg_tp, choice_msg_tp)

    df["send_msg_type"] = df.apply(lambda x: convert_send_msg_type(x), axis=1)

    # 하단 문구 추가
    cond_bottom_txt = [
        (df["send_msg_type"].isin(["sms", "lms", "mms"])),  # 문자메세지
        ~(df["send_msg_type"].isin(["sms", "lms", "mms"])),  # 문자메세지 x
    ]

    choice_bottom_text = [df["send_msg_body"] + "\n\n" + df["bottom_text"], df["send_msg_body"]]

    df["send_msg_body"] = np.select(cond_bottom_txt, choice_bottom_text)

    return df
