import uuid

from src.payment.routes.use_case.key_generator import KeyGenerator


class TossUUIDKeyGenerator(KeyGenerator):

    @staticmethod
    def generate(prefix: str | None = None) -> str:
        new_uuid = str(uuid.uuid4())

        if prefix:
            return f"{prefix.upper()}_{new_uuid}"

        return new_uuid
