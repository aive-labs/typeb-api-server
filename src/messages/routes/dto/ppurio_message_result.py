from typing import Optional

from pydantic import BaseModel, Field


class PpurioMessageResult(BaseModel):
    DEVICE: str = Field(..., description="메시지 유형")
    CMSGID: str = Field(..., description="메시지 키")
    MSGID: str = Field(..., description="비즈뿌리오 메시지 키")
    PHONE: str = Field(..., description="수신 번호")
    MEDIA: str = Field(..., description="실제 발송된 메시지 상세 유형 * MEDIA 유형")
    TO_NAME: Optional[str] = Field(None, description="수신자 명")
    UNIXTIME: str = Field(..., description="발송 시간")
    RESULT: str = Field(
        ..., description="이통사/카카오/RCS 결과 코드 * 발송 결과 코드 참조"
    )
    USERDATA: Optional[str] = Field(None, description="정산용 부서 코드")
    WAPINFO: Optional[str] = Field(
        None, description="이통사/카카오 정보 * SKT/KTF/LGT/KAO"
    )
    TELRES: Optional[str] = Field(None, description="이통사 대체 발송 결과")
    TELTIME: Optional[str] = Field(None, description="이통사 대체 발송 시간")
    KAORES: Optional[str] = Field(None, description="카카오 대체 발송 결과")
    KAOTIME: Optional[str] = Field(None, description="카카오 대체 발송 시간")
    RCSRES: Optional[str] = Field(None, description="RCS 대체 발송 결과")
    RCSTIME: Optional[str] = Field(None, description="RCS 대체 발송 시간")
    RETRY_FLAG: Optional[str] = Field(None, description="대체 발송 정보")
    RESEND_FLAG: Optional[str] = Field(None, description="대체 발송 메시지 유형")
    REFKEY: Optional[str] = Field(None, description="고객사에서 부여한 키")
