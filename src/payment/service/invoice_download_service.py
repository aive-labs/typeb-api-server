from datetime import datetime

import pytz
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from weasyprint import HTML

from src.core.exceptions.exceptions import ConsistencyException, ConvertException
from src.payment.enum.charging_type import ChargingType

# from weasyprint import HTML
from src.payment.routes.use_case.invoice_download_usecase import InvoiceDownloadUseCase
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.payment.service.port.base_deposit_repository import BaseDepositRepository
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.users.domain.user import User


class InvoiceDownloadService(InvoiceDownloadUseCase):

    def __init__(
        self,
        payment_repository: BasePaymentRepository,
        credit_repository: BaseCreditRepository,
        deposit_repository: BaseDepositRepository,
    ):
        self.payment_repository = payment_repository
        self.credit_repository = credit_repository
        self.deposit_repository = deposit_repository

    def exec(self, credit_history_id, user: User, db: Session) -> bytes | None:
        tz = "Asia/Seoul"
        today = datetime.now(pytz.timezone(tz)).strftime("%B %-d, %Y")
        credit_history = self.credit_repository.get_credit_history_by_id(credit_history_id, db)

        items = []
        total = 0
        if credit_history.charging_type == ChargingType.PAYMENT.value:
            payment = self.payment_repository.get_payment_by_credit_history_id(
                credit_history_id, db
            )
            item = {
                "charge": format(payment.total_amount, ","),
                "title": credit_history.description,
            }
            total += payment.total_amount
            items.append(item)
        elif credit_history.charging_type == ChargingType.DEPOSIT.value:
            pending_deposit = self.deposit_repository.get_deposit_by_credit_history_id(
                credit_history_id, db
            )
            item = {
                "charge": format(pending_deposit.price, ","),
                "title": credit_history.description,
            }
            total += pending_deposit.price
            items.append(item)
        else:
            raise ConsistencyException(
                detail={"message": "인보이스 다운로드 중 문제가 발생했습니다."}
            )

        # 데이터 추출
        from_addr = {
            "addr1": "서울특별시 용산구 서빙고로 17",
            "addr2": "23층 2309호",
            "company_name": "에이브랩스",
        }
        to_addr = {
            "company_name": "안다르",
            "person_email": "client@example.com",
            "person_name": "김철수",
        }
        invoice_number = f"INVOICE_{credit_history_id}"
        total = format(total, ",")

        # Jinja2 환경 설정
        template_dir = "src/payment/resources/templates"  # 템플릿 디렉토리
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("invoice_template.html")

        print(items)

        # 템플릿 렌더링
        rendered = template.render(
            date=today,
            from_addr=from_addr,
            to_addr=to_addr,
            items=items,
            total=total,
            invoice_number=invoice_number,
        )

        html = HTML(string=rendered)
        pdf_file = html.write_pdf()

        if pdf_file is None:
            raise ConvertException(detail={"messsage": "인보이스 처리 중 문제가 발생했습니다."})

        return pdf_file
