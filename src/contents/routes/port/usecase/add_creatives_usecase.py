from abc import ABC, abstractmethod


class AddCreativesUseCase(ABC):

    @abstractmethod
    async def upload_image(self):
        pass
