from abc import ABC, abstractmethod


class KeyGenerator(ABC):

    @abstractmethod
    def exec(self, prefix: str | None = None) -> str:
        pass
