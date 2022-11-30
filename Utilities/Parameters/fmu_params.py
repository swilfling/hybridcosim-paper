from dataclasses import dataclass
from .parameters import Parameters


@dataclass
class FMU_src_paths(Parameters):
    """
    FMU source paths
    """
    src_dirs: dict = None
    src_files: dict = None
    resource_dirs: dict = None
    resource_root: str = ""
    src_root: str = ""
    resource_dst: str = "models"

