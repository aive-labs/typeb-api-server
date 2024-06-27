from functools import wraps

from fastapi import HTTPException
from sqlalchemy import text


def transactional(func):
    @wraps(func)
    def wrap_func(*args, **kwargs):
        user = kwargs.get("user")
        if user is None:
            raise HTTPException(
                status_code=500, detail={"message": "서버 내부 문제가 발생했습니다."}
            )

        new_session = kwargs.get("db")
        if new_session is None:
            raise HTTPException(
                status_code=500, detail={"message": "서버 내부 문제가 발생했습니다."}
            )

        print(f"db_session: {new_session}")
        print("in @transanctional")

        try:
            print(f"[in transaction] SET search_path TO {user.mall_id}")
            new_session.execute(text(f"SET search_path TO {user.mall_id}"))
            new_session.commit()

            result = new_session.execute(text("SHOW search_path")).fetchone()
            print(f"Current search_path: {result}")

            result = func(*args, **kwargs)
            new_session.commit()
            print("transaction commit")
        except Exception as e:
            new_session.rollback()
            raise e
        finally:
            new_session.close()
            print("transaction close")

        return result

    return wrap_func
