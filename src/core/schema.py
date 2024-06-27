from contextvars import ContextVar

schema_context: ContextVar[str | None] = ContextVar[str | None](
    "schema_context", default=None
)
