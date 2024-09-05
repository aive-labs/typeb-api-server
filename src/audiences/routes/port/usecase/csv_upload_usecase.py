from abc import ABC, abstractmethod


class CSVUploadUseCase(ABC):

    @abstractmethod
    def check_audience_csv_file(self, uploaded_rows, template_enum) -> tuple:
        pass
