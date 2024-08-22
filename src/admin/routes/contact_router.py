import psycopg2
from fastapi import APIRouter, status

from src.admin.routes.dto.request.contact_us_request import ContactUsRequest
from src.common.utils.get_env_variable import get_env_variable

contact_router = APIRouter(tags=["Contact Us"])


@contact_router.post("")
def contact_us_from_home(contact_us_request: ContactUsRequest):
    db_conn = psycopg2.connect(
        dbname=get_env_variable("user_db_name"),
        user=get_env_variable("user_db_user"),
        password=get_env_variable("user_db_password"),
        host=get_env_variable("user_db_host"),
        port=get_env_variable("user_db_port"),
    )

    try:
        with db_conn.cursor() as cursor:
            insert_query = """
                 INSERT INTO public.contact_us (name, email, phone, message)
                 VALUES (%s, %s, %s, %s)
             """
            cursor.execute(
                insert_query,
                (
                    contact_us_request.name,
                    contact_us_request.email,
                    contact_us_request.phone,
                    contact_us_request.message,
                ),
            )
            db_conn.commit()  # 데이터베이스에 변경사항을 커밋
    except Exception as e:
        db_conn.rollback()  # 오류 발생 시 롤백
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "등록 요청에 실패하였습니다."},
        )
    finally:
        db_conn.close()
