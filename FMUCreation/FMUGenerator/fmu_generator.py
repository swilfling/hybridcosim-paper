import os
import shutil
from distutils.dir_util import copy_tree
import zipfile
from pathlib import Path
import unifmu.generate
from Data.DataImport.featureset import FeatureSet
from .xml_parser import FMUXMLParser


class FMUGenerator:
    """
    Generate an FMU using the UniFMU package.
    Parameters:
        fmu_name: name for created FMU
        fmu_src_dir: directory for sources included in FMU creation
        fmu_output_dir: Output directory for generated FMU
        fmu_interface: inputs and outputs
    """
    fmu_name: str = None
    fmu_src_dir: str = None
    fmu_output_dir: str = None
    fmu_interface: FeatureSet = None

    def __init__(self, fmu_name, fmu_src_dir, fmu_output_dir, fmu_interface):
        self.fmu_name = fmu_name
        self.fmu_src_dir = fmu_src_dir
        self.fmu_output_dir = fmu_output_dir
        self.fmu_interface = fmu_interface

    def create_FMU(self):
        """
        Create FMU.
        Steps:
        - generate FMU source tree
        - copy FMU sources to source tree
        - rewrite XML model description
        - Compress files
        """
        FMU_directory = Path(self.fmu_output_dir) / "FMU"
        output_path = Path(self.fmu_output_dir) / f'{self.fmu_name}'
        fmu_path = output_path.with_suffix('.fmu')
        # Remove old fmu
        fmu_path.unlink(missing_ok=True)
        # Generate tree, adapt files
        self._generate_FMU_tree(FMU_directory)
        copy_tree(self.fmu_src_dir, str(FMU_directory / "resources"))
        xml_parser = FMUXMLParser(str(FMU_directory / "modelDescription.xml"))
        xml_parser.exportxml(self.fmu_interface)
        # Compress directory and rename
        self._zipdir(FMU_directory, output_path, files_to_omit=["__pycache__", ".pyc"])
        output_path.rename(fmu_path)
        shutil.rmtree(FMU_directory)

    def _generate_FMU_tree(self, FMU_directory):
        """
        Generate basic tree for FMU using the UniFMU 0.0.3 backend.
        @param FMU_directory: directory to create tree in
        """
        Path(FMU_directory).unlink(missing_ok=True)
        unifmu.generate.generate_fmu_from_backend("python", FMU_directory)

    @staticmethod
    def _zipdir(src_path, zipfile_path, files_to_omit=None):
        """
        Compress contents of directory
        @param src_path: directory to compress
        @param zipfile_path: Output path for zipfile
        @param files_to_omit: omit these filenames in zipping
        """
        with zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if all([to_omit not in file for to_omit in files_to_omit]):
                        print("Compressing:", str(file))
                        path_file = os.path.join(root, file)
                        zipf.write(path_file, os.path.relpath(path_file, src_path))
