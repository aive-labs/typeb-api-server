from functools import wraps

from fastapi import HTTPException


def transactional(func):
    @wraps(func)
    def wrap_func(*args, **kwargs):
        new_session = kwargs.get("db")
        if new_session is None:
            raise HTTPException(
                status_code=500,
                detail={"message": "서버 내부 문제가 발생했습니다. 관리자에게 문의하세요."},
            )

        print(f"[in transaction] db_session: {new_session}")

        try:
            result = func(*args, **kwargs)
            new_session.commit()
            print("[in transaction] transaction commit")
        except Exception as e:
            new_session.rollback()
            raise e
        finally:
            new_session.close()
            print("[in transaction] transaction close")

        return result

    return wrap_func
