import os
from pathlib import Path
from dataclasses import dataclass
from .parameters import Parameters


@dataclass
class Directories(Parameters):
    """
    Base class for directories
    """
    root_dir: str = ""

    @staticmethod
    def _abspath(path, is_abspath=False, is_pythonpath=False):
        """
        Create absolute path
        @param is_abspath: return absolute path
        @param is_pythonpath: return Path object
        @return: path
        """
        abspath = os.path.abspath(path) if is_abspath else path
        return Path(abspath) if is_pythonpath else abspath

    def get_paths(self, abspath=False):
        """
        Return all paths
        @param abspath: return absolute paths
        @return: list of paths
        """
        return []

    def create_directories(self, rootdir=""):
        """
        Create directory structure in root directory
        @param rootdir: root directory (string)
        """
        for path in self.get_paths_from_rootdir(rootdir):
            os.makedirs(path, exist_ok=True)

    def get_paths_from_rootdir(self, rootdir="", abspath=True):
        """
        Get paths from directory - specify root directory
        instead of using internal root directory
        @param rootdir: root directory
        @param abspath: select absolute path
        @return: relative paths
        """
        return [self._abspath(os.path.join(rootdir, item), abspath) for item in self.get_paths()]

    @staticmethod
    def create_directory_structure(directories=None):
        """
        Create directory structure
        @param directories: list of paths
        """
        for path in directories:
            os.makedirs(path, exist_ok=True)