from contextvars import ContextVar

schema_context: ContextVar[str | None] = ContextVar[str | None](
    "schema_context", default=None
)


def set_current_schema(schema_name: str):
    print(f"Setting Current Schema: {schema_name}")
    schema_context.set(schema_name)


def get_current_schema() -> str:
    schema = schema_context.get()
    print(f"Getting Current Schema: {schema}")
    if schema is None:
        return "aivelabs_sv"
    return schema
