from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class PpurioMessageResultEntity(Base):
    __tablename__ = "ppurio_message_results"

    id = Column(Integer, primary_key=True, index=True)
    DEVICE = Column("device", String, nullable=False, comment="메시지 유형")
    CMSGID = Column("cmsgid", String, nullable=False, comment="메시지 키")
    MSGID = Column("msgid", String, nullable=False, comment="비즈뿌리오 메시지 키")
    PHONE = Column("phone", String, nullable=False, comment="수신 번호")
    MEDIA = Column(
        "media",
        String,
        nullable=False,
        comment="실제 발송된 메시지 상세 유형 * MEDIA 유형",
    )
    TO_NAME = Column("to_name", String, nullable=True, comment="수신자 명")
    UNIXTIME = Column("unixtime", String, nullable=False, comment="발송 시간")
    RESULT = Column(
        "result",
        String,
        nullable=False,
        comment="이통사/카카오/RCS 결과 코드 * 발송 결과 코드 참조",
    )
    USERDATA = Column("userdata", String, nullable=True, comment="정산용 부서 코드")
    WAPINFO = Column(
        "wapinfo", String, nullable=True, comment="이통사/카카오 정보 * SKT/KTF/LGT/KAO"
    )
    TELRES = Column("telres", String, nullable=True, comment="이통사 대체 발송 결과")
    TELTIME = Column("teltime", String, nullable=True, comment="이통사 대체 발송 시간")
    KAORES = Column("kaores", String, nullable=True, comment="카카오 대체 발송 결과")
    KAOTIME = Column("kaotime", String, nullable=True, comment="카카오 대체 발송 시간")
    RCSRES = Column("rcsres", String, nullable=True, comment="RCS 대체 발송 결과")
    RCSTIME = Column("rcstime", String, nullable=True, comment="RCS 대체 발송 시간")
    RETRY_FLAG = Column("retry_flag", String, nullable=True, comment="대체 발송 정보")
    RESEND_FLAG = Column("resend_flag", String, nullable=True, comment="대체 발송 메시지 유형")
    REFKEY = Column("refkey", String, nullable=True, comment="고객사에서 부여한 키")
    send_resv_seq = Column(Integer, nullable=True)
    created_at = Column("created_at", DateTime(timezone=True), default=func.now())
    updated_at = Column(
        "updated_at",
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )
