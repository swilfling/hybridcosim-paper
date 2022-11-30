import os
from dataclasses import dataclass
from .directories import Directories
from pathlib import Path


@dataclass
class ExperimentDirectoryStructure(Directories):
    """
    Directory structure for experiment
    - Training results
        - models
    - FMU
    - Dymola
        - testbench
    """
    training_results_dir: str = ""
    FMU_dir: str = ""
    dymola_main_dir: str = ""
    testbench_dir: str = ""
    models_dir: str = ""

    def get_train_results_path(self, abspath=False, is_pythonpath=False):
        """
        Get path to training results dir
        @param abspath: return absolute path
        @param is_pythonpath: return Path object
        @return: path
        """
        return self._abspath(Path(self.root_dir) / self.training_results_dir, abspath, is_pythonpath)

    def get_models_path(self, abspath=False, is_pythonpath=False):
        """
            Get path to training results dir
            @param abspath: return absolute path
            @param is_pythonpath: return Path object
            @return: path
        """
        path = Path(self.root_dir) / self.training_results_dir / self.models_dir
        return self._abspath(path, abspath, is_pythonpath)

    # Get path to FMU main dir
    def get_FMU_path(self, abspath=False, is_pythonpath=False):
        """
           Get path to FMU dir
           @param abspath: return absolute path
           @param is_pythonpath: return Path object
           @return: path
        """
        path = Path(self.root_dir) / self.FMU_dir
        return self._abspath(path, abspath, is_pythonpath)

    def get_dymola_main_path(self, abspath=False, is_pythonpath=False):
        """
           Get path to Dymola main dir
           @param abspath: return absolute path
           @param is_pythonpath: return Path object
           @return: path
        """
        path = Path(self.root_dir) / self.dymola_main_dir
        return self._abspath(path, abspath, is_pythonpath)

    def get_testbench_path(self, abspath=False, is_pythonpath=False):
        """
           Get path to Testbench dir
           @param abspath: return absolute path
           @param is_pythonpath: return Path object
           @return: path
        """
        path = Path(self.root_dir) / self.dymola_main_dir / self.testbench_dir
        return self._abspath(path, abspath, is_pythonpath)

    # Get all paths in directory structure
    def get_paths(self, abspath=False):
        """
            Get all paths
            @param abspath: get absolute paths
            @return: list of paths
        """
        directories = [self.root_dir]
        # Define main directories
        for item in [self.training_results_dir, self.FMU_dir, self.dymola_main_dir]:
            path_from_root = os.path.join(self.root_dir, item)
            directories.append(path_from_root)
        # Define FMU Testing directories
        for item in [self.testbench_dir]:
            path_from_root = os.path.join(self.root_dir, self.dymola_main_dir, item)
            directories.append(path_from_root)
        for item in [self.models_dir]:
            path_from_root = os.path.join(self.root_dir, self.training_results_dir, item)
            directories.append(path_from_root)
        return directories
