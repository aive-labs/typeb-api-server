from abc import ABC, abstractmethod


class AudienceUpdateCycleUseCase(ABC):

    @abstractmethod
    def exec(self, audience_id: str, update_cycle: str):
        pass
