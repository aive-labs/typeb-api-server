from contextvars import ContextVar

# correlation_id 컨텍스트 변수 생성
correlation_id_var: ContextVar[str] = ContextVar("correlation_id")
