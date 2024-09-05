from abc import ABC, abstractmethod


class KeyGenerator(ABC):

    @staticmethod
    @abstractmethod
    def generate(prefix: str | None = None) -> str:
        pass
