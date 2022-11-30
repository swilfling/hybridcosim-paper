from dataclasses import dataclass
from typing import List
from . parameters import Parameters

@dataclass
class DymolaModelParameters(Parameters):
    model_name: str = ""
    parameters: dict = None
    fmu_path: str = ""
    inputs: dict = None # Inputs with mapping to a variable
    outputs: List[str] = None
    instance_name: str = "UUT"
    is_fmu: bool = False
    is_exchange_model: bool = False
    is_initial_exchange_model: bool = False
    package_paths: List[str] = None # List of all package paths
    use_fmi_init_params: bool = False

    def get_input_names(self):
        """
        Get names of inputs
        @return: list of input names
        """
        return list(self.inputs.keys()) if self.inputs else []
