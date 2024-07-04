from abc import ABC, abstractmethod


class UpdateAudienceExcludeStatusUseCase(ABC):

    @abstractmethod
    def exec(self, audience_id, is_exclude, user):
        pass
