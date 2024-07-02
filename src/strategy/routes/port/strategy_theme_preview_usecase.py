from abc import ABC, abstractmethod


class StrategyThemePreviewUseCase(ABC):

    @abstractmethod
    def get_strategy_theme_preview(self):
        pass
