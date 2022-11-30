import os
import shutil
from datetime import datetime
from pathlib import Path
from distutils.dir_util import copy_tree


def create_gitignore(dst_dir):
    """
    Create a gitignore file in destination directory
    :param dst_dir: destination dir
    """
    create_file(os.path.join(dst_dir, ".gitignore"), "**")


def create_file(file_path_full, lines):
    """
    Create file
    :param file_path_full: path to file
    :param lines: lines to write
    """
    if lines:
        with open(file_path_full, "w") as f:
            f.writelines(lines)


def move_model(file_paths, dst_dir):
    """
    Move trained model to destination directory to create FMU
    Copy:
    - model file (model.py)
    - trained models (Pickle files)
    - additional sources (separate files)
    - additional directories (recursively)
    :param file_paths: fmu srcs object
    :param dst_dir: destination directory (str)
    """
    src_root = Path(file_paths.src_root)
    dst_root = Path(dst_dir)
    # Remove old files
    shutil.rmtree(dst_root, ignore_errors=True)
    os.makedirs(dst_root, exist_ok=True)
    # Copy additional sources to resources path
    dst_paths = [Path(path) for path in file_paths.src_files.keys()]
    for dir_ in [path.parent for path in dst_paths]:
        os.makedirs(dst_root / dir_, exist_ok=True)
    # Copy additional sources
    for src_path, dst_path in zip(file_paths.src_files.values(), dst_paths):
        shutil.copy(str(src_root / src_path), str(dst_root / dst_path))
    # Copy source directories to resources path
    for path in file_paths.src_dirs:
        copy_tree(str(src_root / path), str(dst_root / os.path.split(path)[-1]))
    # Copy Pickle model and parameters for each feature
    res_dst = dst_root / file_paths.resource_dst
    resource_root = Path(file_paths.resource_root)
    for src, dst in file_paths.resource_dirs.items():
        shutil.copytree(resource_root / src, res_dst / dst, dirs_exist_ok=True)
    # Create gitignore in dst dir
    create_gitignore(dst_dir)


def create_file_name_timestamp():
    """
    Create file name using current timestamp
    @return: file name
    """
    return "Experiment_" + datetime.now().strftime("%Y%m%d_%H%M%S")