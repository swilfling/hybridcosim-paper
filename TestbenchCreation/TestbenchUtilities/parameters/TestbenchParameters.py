from dataclasses import dataclass
from .parameters import Parameters

@dataclass
class TestbenchParameters(Parameters):
    package_file_name: str = ""
    data_text_file_name: str = ""
    package_name: str = ""
    model_name: str = ""
    FMU_name: str = ""
    combitable_name: str = ""
    datatable_name: str = "data"
    num_init_samples: int = 4

    def full_name(self):
        """
        @return: full package name
        """
        return f"{self.package_name}.{self.model_name}"
