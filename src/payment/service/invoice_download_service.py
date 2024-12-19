from datetime import datetime

import pytz
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from weasyprint import HTML

from src.common.utils.date_utils import format_datetime
from src.main.exceptions.exceptions import ConsistencyException, ConvertException
from src.payment.model.charging_type import ChargingType
from src.payment.model.credit_status import CreditStatus

# from weasyprint import HTML
from src.payment.routes.use_case.invoice_download_usecase import InvoiceDownloadUseCase
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.payment.service.port.base_deposit_repository import BaseDepositRepository
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.user.domain.user import User


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
        korea_tz = pytz.timezone("Asia/Seoul")
        today = datetime.now(korea_tz).strftime("%Y-%m-%d %H:%M:%S")
        credit_history = self.credit_repository.get_credit_history_by_id(credit_history_id, db)

        if credit_history.status == CreditStatus.REFUND.value:
            purchase_or_cancel = "취소"
        elif credit_history.status == CreditStatus.CHARGE_COMPLETE.value:
            purchase_or_cancel = "구매"
        else:
            raise ConsistencyException(
                detail={"message": "구매, 환불에 대해서만 영수증 다운로드가 가능합니다."}
            )

        items = []
        total = 0
        if credit_history.charging_type == ChargingType.PAYMENT.value:
            payment = self.payment_repository.get_payment_by_credit_history_id(
                credit_history_id, db
            )
            item = self.extract_receipt_info_from_payment(
                credit_history, payment, purchase_or_cancel
            )
            total += payment.total_amount
            items.append(item)
        elif credit_history.charging_type == ChargingType.DEPOSIT.value:
            pending_deposit = self.deposit_repository.get_deposit_by_credit_history_id(
                credit_history_id, db
            )

            item = self.extract_receipt_info_from_deposit(
                credit_history, korea_tz, pending_deposit, purchase_or_cancel
            )
            total += pending_deposit.price
            items.append(item)
        else:
            raise ConsistencyException(
                detail={"message": "인보이스 다운로드 중 문제가 발생했습니다."}
            )

        invoice_number = f"RCPT-{str(credit_history_id).zfill(7)}"
        total = format(total, ",")

        # Jinja2 환경 설정
        template_dir = "src/payment/resources/templates"  # 템플릿 디렉토리
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("receipt_template.html")

        # 템플릿 렌더링
        rendered = template.render(
            date=today,
            items=items,
            total=total,
            invoice_number=invoice_number,
        )

        html = HTML(string=rendered)

        pdf_file = html.write_pdf()

        if pdf_file is None:
            raise ConvertException(detail={"messsage": "인보이스 처리 중 문제가 발생했습니다."})

        return pdf_file

    def extract_receipt_info_from_deposit(
        self, credit_history, korea_tz, pending_deposit, purchase_or_cancel
    ):
        item = {
            "charge": format(pending_deposit.price, ","),
            "title": credit_history.description,
            "payment_type": "무통장 입금",
            "depositor": pending_deposit.depositor,
            "purchase_or_cancel": purchase_or_cancel,
            "approved_at": (
                pending_deposit.updated_at.astimezone(korea_tz).strftime("%Y-%m-%d %H:%M:%S")
                if pending_deposit.updated_at
                else None
            ),
        }
        return item

    def extract_receipt_info_from_payment(self, credit_history, payment, purchase_or_cancel):
        item = {
            "method": payment.method.value,
            "card_company": payment.card_company,
            "card_number": payment.card_number,
            "approved_at": (
                format_datetime(payment.approved_at)
                if payment.cancel_at is None
                else payment.cancel_at
            ),
            "purchase_or_cancel": purchase_or_cancel,
            "charge": format(payment.total_amount, ","),
            "title": credit_history.description,
            "payment_type": "간편결제",
        }
        return item
