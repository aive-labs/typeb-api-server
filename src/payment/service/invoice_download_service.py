from datetime import datetime

import pytz
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from weasyprint import HTML

from src.core.exceptions.exceptions import ConvertException
from src.payment.routes.use_case.invoice_download_usecase import InvoiceDownloadUseCase
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.users.domain.user import User


class InvoiceDownloadService(InvoiceDownloadUseCase):

    def __init__(self, payment_repository: BasePaymentRepository):
        self.payment_repository = payment_repository

    def exec(self, order_id, user: User, db: Session) -> bytes:
        tz = "Asia/Seoul"
        today = datetime.now(pytz.timezone(tz)).strftime("%B %-d, %Y")
        # payment = self.payment_repository.get_payment_by_order_id(order_id, db)

        default_data = {
            "duedate": "August 1, 2019",
            "from_addr": {
                "addr1": "12345 Sunny Road",
                "addr2": "Sunnyville, CA 12345",
                "company_name": "Python Tip",
            },
            "invoice_number": 123,
            "items": [
                {"charge": 300.0, "title": "website design"},
                {"charge": 75.0, "title": "Hosting (3 months)"},
                {"charge": 10.0, "title": "Domain name (1 year)"},
            ],
            "to_addr": {
                "company_name": "Acme Corp",
                "person_email": "john@example.com",
                "person_name": "John Dilly",
            },
        }

        # 데이터 추출
        duedate = default_data["duedate"]
        from_addr = default_data["from_addr"]
        to_addr = default_data["to_addr"]
        items = default_data["items"]
        invoice_number = default_data["invoice_number"]

        total = sum([i["charge"] for i in items])

        # Jinja2 환경 설정
        template_dir = "src/payment/resources/templates"  # 템플릿 디렉토리
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("invoice_template.html")

        # 템플릿 렌더링
        rendered = template.render(
            date=today,
            from_addr=from_addr,
            to_addr=to_addr,
            items=items,
            total=total,
            invoice_number=invoice_number,
            duedate=duedate,
        )

        html = HTML(string=rendered)
        pdf_file = html.write_pdf()

        if pdf_file is None:
            raise ConvertException(detail={"messsage": "인보이스 처리 중 문제가 발생했습니다."})

        return pdf_file
